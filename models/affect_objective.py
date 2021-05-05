import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models, transforms

class AffectObjective(nn.Module):
    EMOTION_DICT = {
        0: "angry",
        1: "disgust",
        2: "fear",
        3: "happy",
        4: "sad",
        5: "surprise",
        6: "neutral",
    }
    INPUT_SIZE = 224

    def __init__(self, pretrain_path, desired_affect):
        super(AffectObjective, self).__init__()

        assert desired_affect in self.EMOTION_DICT
        self.pretrain_path = pretrain_path
        self.desired_affect = desired_affect

        self.model = models.densenet121()
        num_ftrs = self.model.classifier.in_features
        self.model.classifier = nn.Linear(num_ftrs, len(self.EMOTION_DICT))

        self.model.load_state_dict(torch.load(pretrain_path, map_location='cpu')['net']) #TODO make this adapt to the device

        self.input_transform = transforms.Compose([
            transforms.ToPILImage(mode=None), # todo confirm that mode should be none or find a way to run transforms w/o conversion

            # color space and pixel depth of input data (optional). If mode is None (default) there are some assumptions made about the input data: 1. If the input has 3 channels, the mode is assumed to be RGB. 2. If the input has 4 channels, the mode is assumed to be RGBA. 3. If the input has 1 channel, the mode is determined by the data type (i,e, int, float, short).

            transforms.Resize(self.INPUT_SIZE),
            transforms.CenterCrop(self.INPUT_SIZE),
            transforms.Grayscale(num_output_channels=3),
            # transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]), TODO confirm if this pretrained densenet requires normalization
            transforms.ToTensor()
        ])

    def forward(self, X):
        """
        :param X: A tensor ([channels, height, width]) of a cropped face image
        :return: A tensor ([]) of the desired class likelihood of the image
        """

        X_transformed = self.input_transform(X)                     # X_transformed ([channels, height, width])
        logits = self.model(X_transformed.unsqueeze(0))                          # logits ([classes])
        likelihoods = F.softmax(logits.squeeze(0), dim=0)                      # likelihoods ([classes])
        desired_likelihoods = likelihoods[self.desired_affect]    # desired_likelihoods ([])

        return desired_likelihoods



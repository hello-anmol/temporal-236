import torch
import torch.nn as nn
import torch.nn.functional as F


class Generator(nn.Module):

    def __init__(self, channels):
        """ Initializes the Generator.

            Args:
                Number of channels for each image in the dataset.

            Returns:
                None
        """

        super(Generator, self).__init__()

        def generator_x_to_z_block(in_channels, out_channels):
            return [
                nn.BatchNorm2d(in_channels),
                nn.Conv2d(in_channels, out_channels, 3, stride=1, padding=1),
                nn.MaxPool2d(2),
            ]

        def generator_z_to_y_block(in_channels, out_channels):
            return [
                nn.LeakyReLU(negative_slope=0.2),
                nn.BatchNorm2d(in_channels, 0.8),
                nn.Upsample(scale_factor=2),
                nn.Conv2d(in_channels, out_channels, 3, stride=1, padding=1),
            ]

        self.x_to_z = nn.Sequential(
            *generator_x_to_z_block(2 * channels, 20),
            *generator_x_to_z_block(20, 40),
            *generator_x_to_z_block(40, 80),
            nn.Tanh(),
        )

        self.z_to_y = nn.Sequential(
            *generator_z_to_y_block(80, 40),
            *generator_z_to_y_block(40, 20),
            *generator_z_to_y_block(20, channels),
            nn.Tanh()
        )

    def forward(self, x):
        z = self.x_to_z(x)
        img = self.z_to_y(z)
        return img


class Discriminator(nn.Module):

    def __init__(self, channels, img_size):
        """ Initializes the Discriminator.

            Args:
                channels: int
                    Number of channels for each image in the dataset.
                img_size: int
                    The size of the images in each spatial dimension.

            Returns:
                None
        """

        super(Discriminator, self).__init__()

        def discriminator_block(in_channels, out_channels, bn=True):
            block = [
                nn.Conv2d(in_channels, out_channels, 3, 2, 1),
                nn.LeakyReLU(0.2),
                nn.Dropout2d(0.25)
            ]
            if bn:
                block.append(nn.BatchNorm2d(out_channels, 0.8))
            return block

        self.model = nn.Sequential(
            *discriminator_block(1, 20),
            *discriminator_block(20, 40),
            *discriminator_block(40, 80)
        )

        ds_size = img_size // 8 # factor of 2 for each block
        self.adv_layer = nn.Sequential(
            nn.Linear(80 * ds_size ** 2, 1),
            nn.Sigmoid()
        )

    def forward(self, img):
        out = self.model(img)
        out = out.view(out.shape[0], -1)
        validity = self.adv_layer(out)
        return validity


def weights_init(m):
    classname = m.__class__.__name__
    if classname.find('Conv') != -1:
        torch.nn.init.normal_(m.weight.data, 0.0, 0.02)
    elif classname.find('BatchNorm2d') != -1:
        torch.nn.init.normal_(m.weight.data, 1.0, 0.02)
        torch.nn.init.constant_(m.bias.data, 0.0)

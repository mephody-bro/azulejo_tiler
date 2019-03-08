import torch
import torch.nn as nn
import numpy as np

from .net import GeneratorNet, DiscriminatorNet
from .helpers import normalize, show


class Trainer:
    def __init__(self, images, config):
        self.config = config
        self.images = normalize(np.stack(images), config)
        self.net_generator, self.net_discriminator = self._init_models(config)

    def train(self):
        optimizer_generator = torch.optim.Adam(self.net_generator.parameters(), lr=2e-4, betas=(.5, .999))
        optimizer_discriminator = torch.optim.Adam(self.net_discriminator.parameters(), lr=2e-4, betas=(.5, .999))

        criterion = nn.BCELoss()
        train_num = len(self.images) - self.config['validation_size']

        for e in range(self.config['epochs']):
            indices = np.random.choice(train_num, self.config['batch_size'])
            image_batch = torch.tensor(self.images[indices], dtype=torch.float).permute(0, 3, 1, 2)

            optimizer_discriminator.zero_grad()
            optimizer_generator.zero_grad()

            real_img_evaluation = self.net_discriminator(image_batch)
            ones = torch.ones_like(real_img_evaluation)
            real_img_loss = criterion(real_img_evaluation, ones)

            random_vectors = torch.rand((self.config['batch_size'], 100, 1, 1))
            fake_images = self.net_generator(random_vectors)
            fake_img_evaluation = self.net_discriminator(fake_images.detach())
            zeros = torch.zeros_like(fake_img_evaluation)
            fake_img_loss = criterion(fake_img_evaluation, zeros)

            if e % 10 == 0:
                print(f"--{e}--")
                print(real_img_evaluation)
                print(fake_img_evaluation)

            loss = real_img_loss + fake_img_loss
            loss.backward()
            optimizer_discriminator.step()

            generator_ones = torch.ones_like(fake_img_evaluation)
            fake_img_evaluation = self.net_discriminator(fake_images)
            generator_loss = criterion(fake_img_evaluation, generator_ones)
            generator_loss.backward()
            optimizer_generator.step()

            if (e+1) % 200 == 0:
                show(image_batch.detach().permute(0, 2, 3, 1), fake_images.detach().permute(0, 2, 3, 1), self.config)

        self._save_models()

    def validate(self):
        pass

    def _save_models(self):
        torch.save(self.net_generator.state_dict(), self.config['g_model_file'])
        torch.save(self.net_discriminator.state_dict(), self.config['d_model_file'])

    @staticmethod
    def _init_models(config):
        net_generator = GeneratorNet()
        net_discriminator = DiscriminatorNet()

        if config['restore']:
            net_generator.load_state_dict(torch.load(config['g_model_file']))
            net_generator.eval()
            net_discriminator.load_state_dict(torch.load(config['d_model_file']))
            net_discriminator.eval()

        return net_generator, net_discriminator

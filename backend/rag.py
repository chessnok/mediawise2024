import torch
from langchain_experimental.open_clip import OpenCLIPEmbeddings
from typing import List

device = torch.device('cuda')


class EmbedModel(OpenCLIPEmbeddings):
    def __init__(self, dev, **kwargs):
        self.device = dev
        super().__init__(**kwargs)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        text_features = []
        for text in texts:
            # Tokenize the text
            tokenized_text = self.tokenizer(text).to(self.device)

            # Encode the text to get the embeddings
            embeddings_tensor = self.model.encode_text(tokenized_text).to(
                'cpu')

            # Normalize the embeddings
            norm = embeddings_tensor.norm(p=2, dim=1, keepdim=True)
            normalized_embeddings_tensor = embeddings_tensor.div(norm)

            # Convert normalized tensor to list and add to the text_features list
            embeddings_list = normalized_embeddings_tensor.squeeze(0).tolist()
            text_features.append(embeddings_list)

        return text_features

    def embed_image(self, uris: List[str]) -> List[List[float]]:
        try:
            from PIL import Image as _PILImage
        except ImportError:
            raise ImportError(
                "Please install the PIL library: pip install pillow")

        # Open images directly as PIL images
        pil_images = [_PILImage.open(uri) for uri in uris]

        image_features = []
        for pil_image in pil_images:
            # Preprocess the image for the model
            preprocessed_image = self.preprocess(pil_image).unsqueeze(0).to(
                self.device)

            # Encode the image to get the embeddings
            embeddings_tensor = self.model.encode_image(preprocessed_image).to(
                torch.device('cpu'))

            norm = embeddings_tensor.norm(p=2, dim=1, keepdim=True)
            normalized_embeddings_tensor = embeddings_tensor.div(norm)

            embeddings_list = normalized_embeddings_tensor.squeeze(0).tolist()

            image_features.append(embeddings_list)

        return image_features

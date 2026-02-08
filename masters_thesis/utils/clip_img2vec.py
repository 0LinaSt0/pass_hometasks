import torch
import open_clip
from PIL import Image
import numpy as np

class Img2VecCLIP:
    def __init__(
        self, 
        pretrained='laion2b_s34b_b79k',
        device='cuda' if torch.cuda.is_available() else 'cpu'
    ):
        self.device = device
        
        # Use best open-clip model for product similarity (beats OpenAI's CLIP)
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            'ViT-B-32', pretrained=pretrained
        )
        self.model.eval()
        self.model.to(self.device)
        
    def getVec(self, img):
        """
        img: numpy RGB [H,W,C] from bbox crop
        Returns: 512-dim L2-normalized embedding
        """
        # Convert numpy array to PIL Image
        if img.dtype != np.uint8:
            img = (img * 255).astype(np.uint8) if img.max() <= 1.0 else img.astype(np.uint8)
        img_pil = Image.fromarray(img)
        
        # Preprocess and encode
        image_input = self.preprocess(img_pil).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            image_features = self.model.encode_image(image_input)
    
            # L2 normalize (essential for cosine similarity clustering)
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        
        return image_features.cpu().numpy()[0]  # 512-dim vector
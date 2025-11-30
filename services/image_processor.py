import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image

class ImageProcessor:
    def __init__(self, checkpoint_path, arch="resnet50", img_size=224, device=None):
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.img_size = img_size

        ckpt = torch.load(checkpoint_path, map_location=self.device)
        self.class_to_idx = ckpt.get("class_to_idx", None)
        if self.class_to_idx is None:
            raise RuntimeError("Checkpoint missing 'class_to_idx'.")

        self.classes = [None] * len(self.class_to_idx)
        for c, i in self.class_to_idx.items():
            self.classes[i] = c
        self.model = self._build_model(arch, len(self.classes))
        self.model.load_state_dict(ckpt["model_state_dict"])
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.Resize(int(img_size * 1.14)),
            transforms.CenterCrop(img_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225]),
        ])

    def _build_model(self, arch, num_classes):
        arch = arch.lower()
        if arch in ["resnet18","resnet34","resnet50","resnet101"]:
            arch_map = {
                "resnet18": models.resnet18,
                "resnet34": models.resnet34,
                "resnet50": models.resnet50,
                "resnet101": models.resnet101,
            }
            model = arch_map[arch](weights=None)
            in_feats = model.fc.in_features
            model.fc = nn.Linear(in_feats, num_classes)
        elif arch == "efficientnet_b0":
            model = models.efficientnet_b0(weights=None)
            in_feats = model.classifier[1].in_features
            model.classifier[1] = nn.Linear(in_feats, num_classes)
        else:
            raise ValueError("Unsupported architecture.")
        
        return model.to(self.device)

    def predict(self, image_path):
        img = Image.open(image_path).convert("RGB")
        x = self.transform(img).unsqueeze(0).to(self.device)

        with torch.no_grad():
            out = self.model(x)
            pred_idx = int(torch.argmax(out, 1).item())

        result = self.classes[pred_idx]
        return result

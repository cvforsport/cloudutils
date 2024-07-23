import os
import subprocess
import wandb

# Connectez-vous à Weights and Biases
wandb.login(key=os.getenv("WANDB_API_KEY"))

# Récupérer les données depuis le stockage d'objets Scaleway
subprocess.run([
    "aws", "configure", "set", "aws_access_key_id", os.getenv("SCW_ACCESS_KEY")
])
subprocess.run([
    "aws", "configure", "set", "aws_secret_access_key", os.getenv("SCW_SECRET_KEY")
])
subprocess.run([
    "aws", "--endpoint-url=https://s3.fr-par.scw.cloud", "s3", "cp",
    f"s3://{os.getenv('SCW_BUCKET_NAME')}/{os.getenv('SCW_DATA_FILE')}", "/app/data"
])

# Exécuter l'entraînement YOLO
subprocess.run([
    "yolo", "task=detect", "mode=train",
    f"model={os.getenv('MODEL_NAME')}",
    "data=/app/data.yaml", "epochs=100",
    "project=/app/results"
])
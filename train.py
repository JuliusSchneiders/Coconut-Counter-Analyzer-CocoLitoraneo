"""
Model Training Entry Point.
Executes the YOLO training pipeline using parameters and hyperparameters
defined in the configuration module.
"""
import config
from ultralytics import YOLO

def run_training_pipeline() -> None:
    """
    Initializes the base model and executes the training loop using 
    settings from config.TRAIN_CONFIG.
    """
    ## === [ MODEL INITIALIZATION ] ===
    # Load the pretrained YOLOv11 Nano model as the starting point
    print("[INIT] Carregando modelo base")
    model = YOLO('yolo11n.pt') 

    print("\n[INFO] Iniciando treinamento modularizado...")
    print(f"[INFO] Parâmetros: {config.TRAIN_CONFIG['epochs']} épocas | Batch {config.TRAIN_CONFIG['batch']}")
    
    ## === [ TRAINING EXECUTION ] ===
    # We explicitly pass the data yaml path here.
    # The ** operator unpacks the TRAIN_CONFIG dictionary into keyword arguments
    results = model.train(
        data='data/Coconut_Detec/data.yaml',
        **config.TRAIN_CONFIG
    )
    
    ## === [ POST-TRAINING REPORT ] ===
    print("\n[SUCESSO] Treinamento finalizado!")
    # results.save_dir contains the absolute path to the output directory
    print(f"[INFO] O melhor modelo foi salvo em: {results.save_dir}/weights/best.pt")

if __name__ == '__main__':
    run_training_pipeline()
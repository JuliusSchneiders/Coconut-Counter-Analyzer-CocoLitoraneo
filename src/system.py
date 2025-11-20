import cv2
import config
from ultralytics import YOLO
from src.qc_analyzer import QCAnalyzer
from src.visualizer import Visualizer

class MegaCoconutSystem:
    """
    Main system controller. Handles video I/O, model inference, 
    object tracking, state management, and orchestrates the QC/Visualization modules.
    """

    def __init__(self) -> None:
        ## === [ INITIALIZATION ] ===
        print(f"[INIT] Carregando modelo: {config.MODEL_PATH}...")
        self.model = YOLO(config.MODEL_PATH)
        
        print(f"[INIT] Abrindo fonte de vídeo: {config.VIDEO_SOURCE}...")
        self.cap = cv2.VideoCapture(config.VIDEO_SOURCE)
        
        # Video properties for time calculation
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
        self.current_frame_num = 0
        
        # Counters
        self.count_down = 0 
        self.count_up = 0   
        
        # Statistics Storage
        self.stats = {
            'Small': 0, 'Medium': 0, 'Large': 0,
            'Good': 0,  'Bad': 0,
            'Intact': 0, 'Cracked': 0
        }
        
        # Tracking History Dictionary
        # Structure: {track_id: {'state': str, 'last_pos': tuple, 'counted': bool}}
        self.track_history = {} 

    def run(self) -> None:
        """
        Main execution loop. Processes video frames, runs inference,
        updates counters, and renders the UI.
        """
        if not self.cap.isOpened(): 
            print("[ERRO CRÍTICO] Falha ao abrir o arquivo de vídeo.")
            return

        # Video dimensions
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        line_y = int(height * config.LINE_POSITION)

        print(f"[INFO] Sistema Iniciado. Linha de Contagem Y={line_y}")
        print("[INFO] Pressione 'q' para encerrar e gerar o relatório.")

        while True:
            ret, frame = self.cap.read()
            if not ret: 
                break
            
            self.current_frame_num += 1

            ## === [ INFERENCE ] ===
            # Using ByteTrack (botsort) and Test Time Augmentation for maximum accuracy
            results = self.model.track(
                frame, 
                augment=True, 
                persist=True, 
                conf=0.1, 
                iou=0.5, 
                imgsz=1280, 
                tracker="botsort.yaml", 
                verbose=False
            )
            
            ## === [ STATIC VISUALS ] ===
            Visualizer.draw_lines(frame, width, line_y, config.OFFSET_PX)

            ## === [ PROCESSING DETECTIONS ] ===
            if results[0].boxes.id is not None:
                # Extract tensor data to CPU lists
                boxes_wh = results[0].boxes.xywh.cpu()
                boxes_xy = results[0].boxes.xyxy.cpu().int().tolist()
                track_ids = results[0].boxes.id.int().cpu().tolist()

                for box_wh, box_xy, track_id in zip(boxes_wh, boxes_xy, track_ids):
                    # Extract geometric data
                    x, y, w, h = box_wh
                    cx, cy = float(x), float(y)
                    area = float(w) * float(h)
                    
                    # Extract ROI (Region of Interest) for QC
                    x1, y1, x2, y2 = box_xy
                    # Clamp coordinates to be within image bounds
                    x1, y1 = max(0, x1), max(0, y1)
                    x2, y2 = min(width, x2), min(height, y2)
                    roi = frame[y1:y2, x1:x2]

                    ## === [ QC ANALYSIS ] ===
                    # Delegate analysis to the QC module
                    size_lbl = QCAnalyzer.get_size_label(area)
                    qual_lbl, _ = QCAnalyzer.analyze_quality_brightness(roi)
                    crack_lbl, crack_score = QCAnalyzer.analyze_cracks(roi)

                    ## === [ STATE MANAGEMENT ] ===
                    # Initialize new objects
                    if track_id not in self.track_history:
                        initial_state = "transition"
                        if cy < (line_y - config.OFFSET_PX): initial_state = "above"
                        elif cy > (line_y + config.OFFSET_PX): initial_state = "below"
                        
                        self.track_history[track_id] = {
                            'state': initial_state, 
                            'last_pos': (cx, cy), 
                            'counted': False
                        }
                        continue

                    # Retrieve historical data
                    track_data = self.track_history[track_id]
                    
                    ## === [ VISUALIZATION ] ===
                    # 1. Direction Arrows
                    prev_x, prev_y = track_data['last_pos']
                    dx, dy = cx - prev_x, cy - prev_y
                    
                    if abs(dy) > 1 or abs(dx) > 1:
                        end_pos = (cx + dx * 10, cy + dy * 10)
                        arrow_color = (0, 255, 255) if dy < 0 else (0, 0, 255) # Yellow=Up, Red=Down
                        Visualizer.draw_arrow(frame, (cx, cy), end_pos, arrow_color)

                    # 2. Bounding Boxes & Labels
                    # Determine box color based on priority: Cracked > Bad > Good
                    if crack_lbl == "Cracked": box_col = (255, 0, 255) # Purple
                    elif qual_lbl == "Bad": box_col = (0, 0, 255)      # Red
                    else: box_col = (0, 255, 0)                        # Green

                    labels = {'size': size_lbl, 'qual': qual_lbl, 'crack': crack_lbl}
                    Visualizer.draw_detection_box(frame, (x1, y1, x2, y2), labels, box_col)

                    ## === [ COUNTING LOGIC ] ===
                    prev_state = track_data['state']
                    curr_state = "transition"
                    
                    # Determine current zone relative to hysteresis lines
                    if cy < (line_y - config.OFFSET_PX): curr_state = "above"
                    elif cy > (line_y + config.OFFSET_PX): curr_state = "below"

                    just_counted = False
                    
                    # Check for state crossing (Top -> Bottom)
                    if prev_state == "above" and curr_state == "below":
                        self.count_down += 1
                        track_data['state'] = "below"
                        just_counted = True
                    
                    # Check for state crossing (Bottom -> Top)
                    elif prev_state == "below" and curr_state == "above":
                        self.count_up += 1
                        track_data['state'] = "above"
                        just_counted = True
                    
                    # Update state if valid (not in transition)
                    elif curr_state != "transition":
                        track_data['state'] = curr_state

                    ## === [ STATS UPDATE ] ===
                    # Update statistics only once per object upon counting
                    if just_counted and not track_data['counted']:
                        self.stats[size_lbl] += 1
                        self.stats[qual_lbl] += 1
                        self.stats[crack_lbl] += 1
                        track_data['counted'] = True
                        print(f"[EVENTO] ID {track_id} Contado: {size_lbl} | {qual_lbl} | {crack_lbl}")

                    # Persist updated data
                    track_data['last_pos'] = (cx, cy)
                    self.track_history[track_id] = track_data

            ## === [ DASHBOARD RENDERING ] ===
            frame = Visualizer.draw_dashboard(
                frame, 
                (self.count_up, self.count_down), 
                self.stats, 
                (self.current_frame_num, self.fps)
            )
            
            cv2.imshow("Coconut Counter System", frame)
            
            # Exit on 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'): 
                break

        # Cleanup
        self.cap.release()
        cv2.destroyAllWindows()
        
        ## === [ FINAL REPORT ] ===
        self.print_final_report()

    def print_final_report(self) -> None:
        """Generates and prints the final operation report to stdout."""
        total_seconds = self.current_frame_num / self.fps
        total_minutes = total_seconds / 60
        
        # Determine dominant flow direction
        if self.count_up > self.count_down:
            main_count, direction = self.count_up, "SUBINDO (Baixo -> Cima)"
        else:
            main_count, direction = self.count_down, "DESCENDO (Cima -> Baixo)"

        # Calculate CPM (Coconuts Per Minute)
        cpm = 0.0
        if total_minutes > 0:
            cpm = main_count / total_minutes

        print("\n" + "="*50)
        print("        RELATÓRIO FINAL DE OPERAÇÃO")
        print("="*50)
        print(f"Duração Total      : {total_minutes:.2f} min")
        print(f"Direção Predominante: {direction}")
        print("-" * 50)
        print(f"PRODUÇÃO TOTAL     : {main_count} cocos")
        print(f"TAXA MÉDIA (CPM)   : {cpm:.2f} cocos/min")
        print("-" * 50)
        print("DETALHAMENTO DE CONTROLE DE QUALIDADE:")
        print(f"  [TAMANHO]")
        print(f"   - Pequenos : {self.stats['Small']}")
        print(f"   - Médios   : {self.stats['Medium']}")
        print(f"   - Grandes  : {self.stats['Large']}")
        print(f"  [QUALIDADE VISUAL]")
        print(f"   - Aprovados (Bom)  : {self.stats['Good']}")
        print(f"   - Reprovados (Ruim): {self.stats['Bad']}")
        print(f"  [INTEGRIDADE ESTRUTURAL]")
        print(f"   - Íntegros : {self.stats['Intact']}")
        print(f"   - Rachados : {self.stats['Cracked']}")
        print("="*50 + "\n")
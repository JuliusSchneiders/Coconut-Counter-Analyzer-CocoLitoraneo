import cv2
import numpy as np

class Visualizer:
    """
    Static utility class responsible for all rendering operations.
    It handles drawing bounding boxes, direction arrows, reference lines,
    and the main statistics dashboard overlay.
    """

    ## === [ SCENE ELEMENTS ] ===
    @staticmethod
    def draw_lines(frame: np.ndarray, width: int, line_y: int, offset: int) -> None:
        """
        Draws the counting line and the hysteresis buffer zone lines.
        
        Args:
            frame (np.ndarray): The current video frame.
            width (int): Frame width.
            line_y (int): Vertical position of the main line.
            offset (int): The buffer zone size (pixels) above and below.
        """
        # Main Counting Line (Blue)
        cv2.line(frame, (0, line_y), (width, line_y), (255, 0, 0), 2)
        
        # Hysteresis Buffer Lines (Cyan/Yellow - Visual guide only)
        # Objects must cross from one buffer line to the other to be counted.
        cv2.line(frame, (0, line_y - offset), (width, line_y - offset), (255, 255, 0), 1)
        cv2.line(frame, (0, line_y + offset), (width, line_y + offset), (255, 255, 0), 1)

    @staticmethod
    def draw_detection_box(frame: np.ndarray, 
                           box_coords: tuple[int, int, int, int], 
                           labels: dict, 
                           box_color: tuple[int, int, int] = (0, 255, 0)) -> None:
        """
        Draws the bounding box and status text for a tracked object.
        """
        x1, y1, x2, y2 = box_coords
        
        # Draw rectangle
        cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)

        # Construct label text: Size | Quality | Crack Status
        label_text = f"{labels['size']} | {labels['qual']}"
        
        if labels['crack'] == "Cracked":
            label_text += " | RACHADO"
            
        # Draw text label above the box
        cv2.putText(frame, label_text, (x1, y1 - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, box_color, 2)

    @staticmethod
    def draw_arrow(frame: np.ndarray, 
                   start_pos: tuple[float, float], 
                   end_pos: tuple[float, float], 
                   color: tuple[int, int, int]) -> None:
        """
        Draws a direction vector arrow indicating object movement.
        """
        cx, cy = start_pos
        ex, ey = end_pos
        
        # tipLength controls the size of the arrow head relative to the line length
        cv2.arrowedLine(frame, (int(cx), int(cy)), (int(ex), int(ey)), 
                        color, 3, tipLength=0.3)

    ## === [ DASHBOARD UI ] ===
    @staticmethod
    def draw_dashboard(frame: np.ndarray, 
                       counts: tuple[int, int], 
                       stats: dict, 
                       fps_data: tuple[int, float]) -> np.ndarray:
        """
        Renders the semi-transparent overlay with real-time statistics.
        
        Args:
            frame (np.ndarray): The original frame.
            counts (tuple): (count_up, count_down).
            stats (dict): Dictionary containing QC statistics.
            fps_data (tuple): (current_frame_number, fps_value).
            
        Returns:
            np.ndarray: A new frame with the dashboard blended in.
        """
        count_up, count_down = counts
        current_frame, fps = fps_data
        
        # Determine Flow Direction & CPM Calculation
        if count_up > count_down:
            fluxo = "SUBINDO"
            color_fluxo = (0, 255, 255) # Yellow
            main_count = count_up
        else:
            fluxo = "DESCENDO"
            color_fluxo = (0, 255, 0)   # Green
            main_count = count_down

        # Coconuts Per Minute Logic
        elapsed_min = (current_frame / fps) / 60
        cpm = main_count / elapsed_min if elapsed_min > 0.01 else 0.0

        # Create Semi-Transparent Overlay
        overlay = frame.copy()
        # Dashboard background rectangle (Top-Left corner)
        cv2.rectangle(overlay, (10, 10), (320, 420), (0, 0, 0), -1)
        
        # Blend overlay with original frame (alpha=0.7)
        frame_final = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)

        # Helper function for cleaner text drawing
        def _put_txt(text: str, pos: tuple[int, int], scale: float = 0.6, color: tuple = (255, 255, 255)):
            cv2.putText(frame_final, text, pos, cv2.FONT_HERSHEY_SIMPLEX, scale, color, 1)

        # --- SECTION 1: PRODUCTION METRICS ---
        _put_txt("PRODUCAO:", (20, 35), color=(200, 200, 200))
        _put_txt(f"Subiram:  {count_up}", (30, 60), scale=0.7)
        _put_txt(f"Desceram: {count_down}", (30, 85), scale=0.7)
        
        cv2.putText(frame_final, f"Fluxo: {fluxo}", (20, 115), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color_fluxo, 2)
        cv2.putText(frame_final, f"CPM: {cpm:.1f}", (20, 145), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        
        # Separator Line
        cv2.line(frame_final, (20, 160), (310, 160), (100, 100, 100), 1)

        # --- SECTION 2: SIZE CLASSIFICATION ---
        _put_txt("TAMANHO (QC):", (20, 185), color=(200, 200, 200))
        _put_txt(f" Peq: {stats['Small']}", (30, 210), color=(100, 255, 255))
        _put_txt(f" Med: {stats['Medium']}", (30, 230), color=(100, 255, 100))
        _put_txt(f" Grd: {stats['Large']}", (30, 250), color=(100, 100, 255))
        
        # Separator Line
        cv2.line(frame_final, (20, 265), (310, 265), (100, 100, 100), 1)

        # --- SECTION 3: QUALITY & DAMAGE ---
        _put_txt("QUALIDADE / DANOS:", (20, 290), color=(200, 200, 200))
        _put_txt(f" BOM:     {stats['Good']}", (30, 315), color=(0, 255, 0))
        _put_txt(f" RUIM:    {stats['Bad']}", (30, 335), color=(0, 0, 255))
        _put_txt(f" RACHADO: {stats['Cracked']}", (30, 355), color=(255, 0, 255))
        _put_txt(f" INTEGRO: {stats['Intact']}", (30, 375), color=(200, 200, 200))

        return frame_final
import cv2
import numpy as np
import config

class QCAnalyzer:
    """
    Stateless utility class responsible for mathematical analysis of image ROIs (Regions of Interest).
    It handles geometry (size), colorimetry (quality), and morphology (cracks).
    """

    ## === QUALITY ANALYSIS (COLOR/BRIGHTNESS) ===
    @staticmethod
    def analyze_quality_brightness(image_roi: np.ndarray) -> tuple[str, float]:
        """
        Analyzes the brightness of the V channel (HSV) to determine if the fruit is healthy.
        
        Args:
            image_roi (np.ndarray): The cropped image of the coconut.
        Returns:
            tuple: Status ('Good'/'Bad') and the calculated brightness value.
        """
        # Safety check for empty frames to avoid crashes
        if image_roi.size == 0:
            return "Unknown", 0.0
        
        # We convert to HSV because the V (Value) channel is more robust 
        # to lighting changes than standard RGB grayscale.
        hsv = cv2.cvtColor(image_roi, cv2.COLOR_BGR2HSV)
        brightness = np.mean(hsv[:, :, 2]) 
        
        # Threshold comparison defined in config
        status = "Good" if brightness >= config.QUALITY_BRIGHTNESS_THRESH else "Bad"
        
        return status, brightness

    ## === STRUCTURAL ANALYSIS (CRACKS) ===
    @staticmethod
    def analyze_cracks(image_roi: np.ndarray) -> tuple[str, float]:
        """
        Detects surface cracks using Morphological Black Hat Transformation.
        This method highlights dark details (cracks) against a brighter background.
        """
        if image_roi.size == 0:
            return "Unknown", 0.0
        
        # Convert to grayscale for morphological processing
        gray = cv2.cvtColor(image_roi, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        # 1. Circular Masking
        # We generate a circular mask to ignore the coconut edges/background,
        # focusing only on the center texture where cracks matter.
        mask = np.zeros((h, w), dtype="uint8")
        mask_radius = int(min(h, w) / 2 * 0.85)
        cv2.circle(mask, (int(w/2), int(h/2)), mask_radius, 255, -1)
        
        # 2. Pre-processing
        # Gaussian Blur removes high-frequency noise (fibers/hair) that could be mistaken for cracks.
        blurred = cv2.GaussianBlur(gray, (7, 7), 0)

        # 3. Black Hat Transform
        # This operation is the difference between the Closing of the input image and the input image itself.
        # It extracts dark objects smaller than the structuring element (15x15 kernel).
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
        blackhat = cv2.morphologyEx(blurred, cv2.MORPH_BLACKHAT, kernel)

        # 4. Thresholding
        # We filter only the pixels that are significantly dark (deep cracks).
        _, thresh = cv2.threshold(blackhat, 30, 255, cv2.THRESH_BINARY)
        thresh_masked = cv2.bitwise_and(thresh, thresh, mask=mask)

        # 5. Density Calculation
        # We calculate the ratio of "crack pixels" vs "total valid pixels".
        crack_pixels = cv2.countNonZero(thresh_masked)
        total_pixels = cv2.countNonZero(mask)
        
        crack_ratio = 0.0
        if total_pixels > 0:
            crack_ratio = crack_pixels / total_pixels

        status = "Intact"
        if crack_ratio > config.CRACK_LIMIT_RATIO:
            status = "Cracked"

        return status, crack_ratio

    ## === GEOMETRIC ANALYSIS ===
    @staticmethod
    def get_size_label(area: float) -> str:
        """
        Classifies the object size based on the bounding box area (pixels^2).
        """
        if area < config.SIZE_THRESHOLDS['small_limit']:
            return "Small"
        elif area < config.SIZE_THRESHOLDS['medium_limit']:
            return "Medium"
        
        return "Large"
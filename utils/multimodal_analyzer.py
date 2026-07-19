"""
Multimodal Image/Video Analyzer for DevPulse.
Analyzes uploaded screenshots and videos for draft quality feedback.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


def analyze_screenshot(image_path: str) -> Dict[str, Any]:
    """
    Analyze screenshot for UI/UX clarity and content structure.
    
    Args:
        image_path: Path to PNG/JPG screenshot
    
    Returns:
        Dict with visual quality assessment
    """
    try:
        from PIL import Image
        
        if not Path(image_path).exists():
            return {"error": "Image file not found"}
        
        img = Image.open(image_path)
        width, height = img.size
        
        # Basic image quality metrics
        analysis = {
            "image_size": (width, height),
            "file_size_mb": Path(image_path).stat().st_size / (1024 * 1024),
            "format": img.format,
            "has_transparency": img.mode == "RGBA",
            "quality_score": calculate_image_quality(width, height),
            "recommendations": []
        }
        
        # Quality recommendations
        if width < 640:
            analysis["recommendations"].append("Image width < 640px - may be too small for readers")
        if height < 400:
            analysis["recommendations"].append("Image height < 400px - content may be hard to read")
        if not analysis["has_transparency"] and img.mode != "RGB":
            analysis["recommendations"].append("Consider using RGB or RGBA format for better compatibility")
        
        logger.info(f"Screenshot analyzed: {width}x{height}")
        return analysis
    
    except Exception as e:
        logger.error(f"Screenshot analysis failed: {e}")
        return {"error": str(e)}


def analyze_video_frame(video_path: str) -> Dict[str, Any]:
    """
    Analyze first frame of video for quality assessment.
    
    Args:
        video_path: Path to MP4/MOV/AVI video
    
    Returns:
        Dict with video quality assessment
    """
    try:
        from pathlib import Path
        import subprocess
        
        if not Path(video_path).exists():
            return {"error": "Video file not found"}
        
        file_size_mb = Path(video_path).stat().st_size / (1024 * 1024)
        
        analysis = {
            "file_size_mb": round(file_size_mb, 2),
            "format": Path(video_path).suffix.lower(),
            "quality_score": calculate_video_quality(file_size_mb),
            "recommendations": []
        }
        
        # File size recommendations
        if file_size_mb > 50:
            analysis["recommendations"].append(f"Video is {file_size_mb}MB - consider compressing for faster loading")
        if file_size_mb < 1:
            analysis["recommendations"].append("Very small video file - verify audio/video quality")
        
        analysis["recommendations"].append("Ensure video has captions for accessibility")
        analysis["recommendations"].append("Verify video plays in all browsers (MP4 recommended)")
        
        logger.info(f"Video analyzed: {file_size_mb}MB")
        return analysis
    
    except Exception as e:
        logger.error(f"Video analysis failed: {e}")
        return {"error": str(e)}


def calculate_image_quality(width: int, height: int) -> float:
    """Calculate image quality score based on dimensions."""
    # Optimal width: 800-1200px
    optimal_width = 1000
    # Optimal aspect ratio: 16:9
    optimal_ratio = 16 / 9
    
    actual_ratio = width / height if height > 0 else 0
    
    width_score = min(100, (width / optimal_width) * 100)
    ratio_diff = abs(actual_ratio - optimal_ratio)
    ratio_score = max(50, 100 - (ratio_diff * 20))
    
    return round((width_score * 0.6 + ratio_score * 0.4), 1)


def calculate_video_quality(file_size_mb: float) -> float:
    """Calculate video quality score based on file size."""
    # Optimal size: 5-20MB (good balance of quality/loading)
    if 5 <= file_size_mb <= 20:
        return 90.0
    elif 1 <= file_size_mb < 5:
        return 70.0
    elif 20 < file_size_mb <= 50:
        return 80.0
    elif file_size_mb > 50:
        return 60.0
    else:
        return 40.0


def generate_visual_feedback(asset_type: str, asset_analysis: Dict) -> str:
    """Generate markdown feedback based on asset analysis."""
    if "error" in asset_analysis:
        return f"⚠️ Could not analyze asset: {asset_analysis['error']}"
    
    feedback = []
    
    if asset_type == "image":
        size = asset_analysis.get("image_size", ())
        quality = asset_analysis.get("quality_score", 0)
        
        feedback.append(f"📸 Image Quality: {quality}/100")
        feedback.append(f"   Dimensions: {size[0]}x{size[1]}px")
        
        if quality >= 80:
            feedback.append("   ✅ Excellent image dimensions for web")
        elif quality >= 60:
            feedback.append("   ⚠️ Could improve image dimensions")
        else:
            feedback.append("   ❌ Image dimensions may be suboptimal")
    
    elif asset_type == "video":
        size_mb = asset_analysis.get("file_size_mb", 0)
        quality = asset_analysis.get("quality_score", 0)
        
        feedback.append(f"🎬 Video Quality: {quality}/100")
        feedback.append(f"   File Size: {size_mb}MB")
        
        if quality >= 80:
            feedback.append("   ✅ Good video file size")
        else:
            feedback.append("   ⚠️ Consider optimizing video size")
    
    # Add recommendations
    for rec in asset_analysis.get("recommendations", []):
        feedback.append(f"   💡 {rec}")
    
    return "\n".join(feedback)


def multimodal_scoring_boost(asset_analysis: Dict, base_score: float) -> float:
    """Calculate scoring boost based on multimodal asset quality."""
    if "error" in asset_analysis:
        return base_score
    
    quality_score = asset_analysis.get("quality_score", 0) or asset_analysis.get("image_size", [0])[0] / 100
    quality_score = min(quality_score, 100)
    
    # Boost: +0 to +10 points based on asset quality
    boost = (quality_score / 100) * 10
    
    return min(100, base_score + boost)

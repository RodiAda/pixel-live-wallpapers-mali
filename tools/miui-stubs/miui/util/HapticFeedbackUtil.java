package miui.util;
import android.content.Context;
import android.net.Uri;
public class HapticFeedbackUtil {
    public HapticFeedbackUtil(Context context, boolean b) {}
    public static boolean isSupportLinearMotorVibrate() { return false; }
    public static boolean isSupportLinearMotorVibrate(int i) { return false; }
    public boolean isSupportExtHapticFeedback(int i) { return false; }
    public boolean performExtHapticFeedback(int i) { return false; }
    public boolean performExtHapticFeedback(Uri uri) { return false; }
    public boolean performHapticFeedback(int i, double d, String s) { return false; }
    public boolean performHapticFeedback(int i, boolean b) { return false; }
    public boolean performHapticFeedback(int i, boolean b, int j) { return false; }
    public void release() {}
}

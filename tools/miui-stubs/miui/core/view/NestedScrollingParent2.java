package miui.core.view;
import android.view.View;
public interface NestedScrollingParent2 extends NestedScrollingParent {
    void onNestedPreScroll(View v, int dx, int dy, int[] consumed, int type);
    void onNestedScroll(View v, int a, int b, int c, int d, int type);
    void onNestedScrollAccepted(View a, View b, int axes, int type);
    boolean onStartNestedScroll(View a, View b, int axes, int type);
    void onStopNestedScroll(View v, int type);
}

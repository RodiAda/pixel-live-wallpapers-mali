package miui.core.view;
import android.view.View;
public interface NestedScrollingParent {
    boolean onNestedFling(View v, float x, float y, boolean c);
    boolean onNestedPreFling(View v, float x, float y);
    void onNestedPreScroll(View v, int dx, int dy, int[] consumed);
    void onNestedScroll(View v, int a, int b, int c, int d);
    void onNestedScrollAccepted(View a, View b, int axes);
    boolean onStartNestedScroll(View a, View b, int axes);
    void onStopNestedScroll(View v);
}

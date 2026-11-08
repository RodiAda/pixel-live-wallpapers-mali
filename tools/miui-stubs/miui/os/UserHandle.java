package miui.os;
public class UserHandle {
    public static int myUserId() { return android.os.Process.myUid() / 100000; }
}

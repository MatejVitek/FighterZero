package manager;

import static org.lwjgl.glfw.Callbacks.*;
import static org.lwjgl.glfw.GLFW.*;
import static org.lwjgl.opengl.GL11.*;
import static org.lwjgl.system.MemoryStack.*;
import static org.lwjgl.system.MemoryUtil.*;

import java.nio.IntBuffer;
import java.util.logging.Level;
import java.util.logging.Logger;

import org.lwjgl.glfw.GLFWErrorCallback;
import org.lwjgl.glfw.GLFWVidMode;
import org.lwjgl.opengl.GL;
import org.lwjgl.system.MemoryStack;

import setting.FlagSetting;
import setting.GameSetting;

/**
 * ă‚˛ă�Ľă� ă�®é€˛čˇŚç®ˇç�†ă‚’čˇŚă�†ă�žă�Ťă�Ľă‚¸ă�Łă‚Żă�©ă‚ąďĽŽ
 */
public class DisplayManager {

	/**
	 * GLFWă�§ä˝żç”¨ă�•ă‚Śă‚‹windowä˝ść��ç”¨ă�®ĺ¤‰ć•°ďĽŽ
	 */
	private long window;

	/**
	 * ă‚Żă�©ă‚ąă‚łă�łă‚ąă��ă�©ă‚Żă‚żďĽŽ
	 */
	public DisplayManager() {

	}

	/**
	 * ă‚˛ă�Ľă� ă‚’ă‚ąă‚żă�Ľă��ă�•ă�›ă‚‹ďĽŽ<br>
	 * 1. OpenGLĺŹŠă�łă‚¦ă‚Łă�łă�‰ă‚¦ă�®ĺ�ťćśźĺŚ–ă‚’čˇŚă�†ďĽŽ<br>
	 * 2. ă‚˛ă�Ľă� ă�®çµ‚äş†ĺ‡¦ç�†ĺ‘˝ä»¤ă�ŚćťĄă‚‹ă�ľă�§ďĽŚă‚˛ă�Ľă� çŠ¶ć…‹ă�®ć›´ć–°ďĽŚćŹŹç”»ĺ‡¦ç�†ă�Şă�©ă�®ă�ˇă‚¤ă�łă�«ă�Ľă�—ĺ‡¦ç�†ă‚’čˇŚă�†ďĽŽ<br>
	 * 3. ă‚˛ă�Ľă� ă�®çµ‚äş†ĺ‡¦ç�†ă‚’čˇŚă�Łă�¦ă‚¦ă‚Łă�łă�‰ă‚¦ă‚’é–‰ă��ă‚‹ďĽŽ<br>
	 *
	 * @param game
	 *            GameManageră‚Żă�©ă‚ąă�®ă‚¤ă�łă‚ąă‚żă�łă‚ą
	 * @see GameManager
	 */
	public void start(GameManager game) {
		// Window, OpenGLă�®ĺ�ťćśźĺŚ–
		initialize();

		// ă�ˇă‚¤ă�łă�«ă�Ľă�—
		gameLoop(game);

		// ă‚˛ă�Ľă� ă�®çµ‚äş†ĺ‡¦ç�†
		close();

	}

	/**
	 * ă‚¦ă‚Łă�łă�‰ă‚¦ă‚’ä˝ść��ă�™ă‚‹éš›ă�®ĺ�ťćśźĺŚ–ĺŹŠă�łOpenGLă�®ĺ�ťćśźĺŚ–ĺ‡¦ç�†ă‚’čˇŚă�†ďĽŽ
	 */
	private void initialize() {
		// Setup an error callback. The default implementation
		// will print the error message in System.err.
		GLFWErrorCallback.createPrint(System.err).set();

		// Initialize GLFW. Most GLFW functions will not work before doing this.
		if (!glfwInit()) {
			throw new IllegalStateException("Unable to initialize GLFW");
		}

		// GLFWă�®č¨­ĺ®š
		glfwDefaultWindowHints();
		glfwWindowHint(GLFW_VISIBLE, GLFW_TRUE);
		glfwWindowHint(GLFW_RESIZABLE, GLFW_FALSE);
		System.setProperty("java.awt.headless", "true");

		// windowă�®ä˝ść��
		short width = GameSetting.STAGE_WIDTH;
		short height = GameSetting.STAGE_HEIGHT;
		this.window = glfwCreateWindow(width, height, "FightingICE", NULL, NULL);
		if (this.window == NULL) {
			throw new RuntimeException("Failed to create the GLFW window");
		}

		// Setup a key callback. It will be called every time a key is pressed,
		// repeated or released.
		glfwSetKeyCallback(this.window, InputManager.getInstance().getKeyboard());

		// Gets the thread stack and push a new frame
		try (MemoryStack stack = stackPush()) {
			IntBuffer pWidth = stack.mallocInt(1); // int*
			IntBuffer pHeight = stack.mallocInt(1); // int*

			// Gets the window size passed to glfwCreateWindow
			glfwGetWindowSize(this.window, pWidth, pHeight);

			// Gets the resolution of the primary monitor
			GLFWVidMode vidmode = glfwGetVideoMode(glfwGetPrimaryMonitor());

			// Center the window
			glfwSetWindowPos(this.window, (vidmode.width() - pWidth.get(0)) / 2,
					(vidmode.height() - pHeight.get(0)) / 2);
		} // the stack frame is popped automatically

		// Makes the OpenGL context current
		glfwMakeContextCurrent(this.window);

		int sync;
		if (!FlagSetting.enableWindow || FlagSetting.fastModeFlag) {
			sync = 0;
		} else {
			sync = 1;
		}

		// Enable v-sync
		glfwSwapInterval(0);


		if (FlagSetting.enableWindow) {
			// Makes the window visible
			glfwShowWindow(this.window);
			Logger.getAnonymousLogger().log(Level.INFO, "Create Window " + width + "x" + height);
		} else {
			// Makes the window invisible
			glfwHideWindow(this.window);
			Logger.getAnonymousLogger().log(Level.INFO, "Disable window mode");
		}
	}

	/**
	 * ă‚˛ă�Ľă� ă�®ă�ˇă‚¤ă�łă�«ă�Ľă�—ă�®ĺ‡¦ç�†ă‚’čˇŚă�†ďĽŽ
	 *
	 * @param gm
	 *            GameManageră‚Żă�©ă‚ąă�®ă‚¤ă�łă‚ąă‚żă�łă‚ą
	 */
	private void gameLoop(GameManager gm) {
		glfwSetTime(0.0);

		// This line is critical for LWJGL's interoperation with GLFW's
		// OpenGL context, or any context that is managed externally.
		// LWJGL detects the context that is current in the current thread,
		// creates the GLCapabilities instance and makes the OpenGL
		// bindings available for use.
		GL.createCapabilities();

		// Sets the clear color
		glClearColor(0.0f, 0.0f, 0.0f, 0.0f);
		initGL();

		// ă‚˛ă�Ľă� ă�žă�Ťă�Ľă‚¸ă�Łĺ�ťćśźĺŚ–
		gm.initialize();

		long lastNanos = System.nanoTime();
		// Runs the rendering loop until the user has attempted to close the
		// window.
		while (!glfwWindowShouldClose(this.window)) {
			// ă‚˛ă�Ľă� çµ‚äş†ă�®ĺ ´ĺ��,ă�Şă‚˝ă�Ľă‚ąă‚’č§Łć”ľă�—ă�¦ă�«ă�Ľă�—ă‚’ćŠśă�‘ă‚‹
			if (gm.isExit()) {
				gm.close();
				break;
			}

			// ă‚˛ă�Ľă� çŠ¶ć…‹ă�®ć›´ć–°
			gm.update();

            syncFrameRate(60, lastNanos);
            lastNanos = System.nanoTime();

			if (FlagSetting.enableWindow) {
				// ă��ă��ă‚Żă��ă��ă�•ă‚ˇă�«ćŹŹç”»ă�™ă‚‹
				GraphicManager.getInstance().render();

				// ă��ă��ă‚Żă��ă��ă�•ă‚ˇă�¨ă�•ă�¬ă�Ľă� ă��ă��ă�•ă‚ˇă‚’ĺ…Ąă‚Ść›żă��ă‚‹
				glfwSwapBuffers(this.window);

				// Poll for window events. The key callback above will only be
				// invoked during this call.
				glfwPollEvents();
			}
		}
	}

	/**
	 * ă‚˛ă�Ľă� ă�®çµ‚äş†ĺ‡¦ç�†ă‚’čˇŚă�„ďĽŚă‚¦ă‚Łă�łă�‰ă‚¦ă‚’é–‰ă��ă‚‹.
	 */
	private void close() {
		GraphicManager.getInstance().close();
		SoundManager.getInstance().close();

		// Free the window callbacks and destroy the window
		glfwFreeCallbacks(this.window);
		glfwDestroyWindow(this.window);

		// Terminate GLFW and free the error callback
		glfwTerminate();
		glfwSetErrorCallback(null).free();
		Logger.getAnonymousLogger().log(Level.INFO, "Close FightingICE");
		System.exit(0);
	}

	/**
	 * OpenGLă�®ĺ�ťćśźĺŚ–ĺ‡¦ç�†ă‚’čˇŚă�†ďĽŽ
	 */
	private void initGL() {
		glMatrixMode(GL_PROJECTION);
		glLoadIdentity();

		glMatrixMode(GL_MODELVIEW);
		glOrtho(0, GameSetting.STAGE_WIDTH, GameSetting.STAGE_HEIGHT, 0, 1, -1);

		// Enable Blending for transparent textures
		glEnable(GL_BLEND);
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
	}

    private void syncFrameRate(float fps, long lastNanos) {
        long targetNanos = lastNanos + (long) (1_000_000_000.0f / fps) - 1_000_000L;  // subtract 1 ms to skip the last sleep call
        try {
            while (System.nanoTime() < targetNanos) {
                Thread.sleep(1);
            }
        }
        catch (InterruptedException ignore) {}
    }
}

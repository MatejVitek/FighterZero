package setting;

import java.util.Random;

import enumerate.BackgroundType;
import python.PyGatewayServer;

/**
 * ã‚­ãƒ£ãƒ©ã‚¯ã‚¿ãƒ¼ã�®æœ€å¤§HPã‚„è©¦å�ˆã�®ç¹°ã‚Šè¿”ã�—å›žæ•°ã�ªã�©ã€�è©¦å�ˆã‚’è¡Œã�†éš›ã�«å¿…è¦�ã�ªè¨­å®šã‚’æ‰±ã�†ã‚¯ãƒ©ã‚¹ï¼Ž
 */
public final class LaunchSetting {

	/**
	 * P1,P2ã�®æœ€å¤§HPã‚’æ ¼ç´�ã�™ã‚‹é…�åˆ—ï¼Ž
	 */
	public static int[] maxHp = { 400, 400 };

	/**
	 * P1,P2ã�®æœ€å¤§ã‚¨ãƒ�ãƒ«ã‚®ãƒ¼ã‚’æ ¼ç´�ã�™ã‚‹é…�åˆ—ï¼Ž
	 */
	public static int[] maxEnergy = { 300, 300 };

	/**
	 * P1,P2ã�®AIå��ã‚’æ ¼ç´�ã�™ã‚‹é…�åˆ—ï¼Ž<br>
	 * ã‚­ãƒ¼ãƒœãƒ¼ãƒ‰ã�®å ´å�ˆã�¯"Keyboard"ã�Œæ ¼ç´�ã�•ã‚Œã‚‹ï¼Ž
	 */
	public static String[] aiNames = { "KeyBoard", "KeyBoard" };

	/**
	 * P1,P2ã�®ã‚­ãƒ£ãƒ©ã‚¯ã‚¿ãƒ¼å��ï¼Ž
	 */
	public static String[] characterNames = {randomCharacter(), randomCharacter()};

	/**
	 * åˆ©ç”¨ã�™ã‚‹ãƒ‡ãƒ�ã‚¤ã‚¹ã‚¿ã‚¤ãƒ—ï¼Ž<br>
	 * {@code 0} if the device type is keyboardï¼Œor {@code 1} if AI.
	 */
	public static char[] deviceTypes = { 0, 0 };

	/**
	 * Pythonã‚’åˆ©ç”¨ã�™ã‚‹ã�¨ã��ã�®ãƒ�ãƒ¼ãƒˆç•ªå�·ï¼Ž
	 */
	public static int py4jPort = 4242;

	/**
	 * è©¦å�ˆã‚’ç¹°ã‚Šè¿”ã�—ã�¦è¡Œã�†å›žæ•°ï¼Ž
	 */
	public static int repeatNumber = 1;

	/**
	 * ç”»ç´ ã‚’å��è»¢ã�•ã�›ã‚‹ãƒ—ãƒ¬ã‚¤ãƒ¤ãƒ¼ã�®ç•ªå�·ï¼Ž
	 */
	public static int invertedPlayer = 0;

	/**
	 * èƒŒæ™¯ã�®ç¨®é¡žï¼Ž
	 */
	public static BackgroundType backgroundType = BackgroundType.IMAGE;

	/**
	 * ãƒªãƒ—ãƒ¬ã‚¤ãƒ‡ãƒ¼ã‚¿ã�®å��å‰�ï¼Ž
	 */
	public static String replayName = "None";

	/**
	 * è©¦å�ˆã�®ç¹°ã‚Šè¿”ã�—å›žæ•°ã�®ã‚«ã‚¦ãƒ³ã‚¿ï¼Ž
	 */
	public static int repeatedCount = 0;

	/**
	 * Pythonã�§Javaã�®å‡¦ç�†ã‚’è¡Œã�†ã�Ÿã‚�ã�®ã‚²ãƒ¼ãƒˆã‚¦ã‚§ã‚¤ã‚µãƒ¼ãƒ�ãƒ¼ï¼Ž
	 */
	public static PyGatewayServer pyGatewayServer = null;
	
	public static String randomCharacter() {
		return GameSetting.CHARACTERS[new Random().nextInt(GameSetting.CHARACTERS.length)];
	}

}

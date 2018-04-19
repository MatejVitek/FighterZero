package python;

import manager.InputManager;
import setting.FlagSetting;
import setting.LaunchSetting;

/**
 * Pythonå�´ã�§è¨­å®šã�—ã�Ÿä½¿ç”¨ã‚­ãƒ£ãƒ©ã‚¯ã‚¿ãƒ¼ã‚„AIå��ã�¨ã�„ã�£ã�Ÿ, ã‚²ãƒ¼ãƒ ã�®èµ·å‹•æƒ…å ±ã‚’æ‰±ã�†ã‚¯ãƒ©ã‚¹.
 */
public class PyGame {

	/**
	 * The character's data of both characters.<br>
	 * Index 0 is P1, index 1 is P2.
	 */
	private String[] characterNames;

	/**
	 * The both AIs' names.<br>
	 * Index 0 is P1, index 1 is P2.
	 */
	private String[] aiNames;

	/**
	 * The number of repeat count of this game.
	 */
	private int num;

	/**
	 * ã‚²ãƒ¼ãƒ ã�Œçµ‚äº†ã�—ã�Ÿã�“ã�¨ã‚’Pythonå�´ã�«çŸ¥ã‚‰ã�›ã‚‹ã�Ÿã‚�ã�®ã‚ªãƒ–ã‚¸ã‚§ã‚¯ãƒˆ.
	 */
	public Object end;

	/**
	 * å¼•æ•°ã�§æŒ‡å®šã�•ã‚Œã�Ÿãƒ‡ãƒ¼ã‚¿ã�§PyGameã�®åˆ�æœŸåŒ–ã‚’è¡Œã�†ã‚¯ãƒ©ã‚¹ã‚³ãƒ³ã‚¹ãƒˆãƒ©ã‚¯ã‚¿ï¼Ž
	 *
	 * @param manager
	 *            ã‚²ãƒ¼ãƒ ã�®ä½œæˆ�ã‚„ãƒªãƒ—ãƒ¬ã‚¤ã�®ãƒ­ãƒ¼ãƒ‰ã�¨ã�„ã�£ã�Ÿå‡¦ç�†ã‚’ç®¡ç�†ã�™ã‚‹ãƒžãƒ�ãƒ¼ã‚¸ãƒ£ãƒ¼
	 * @param c1
	 *            P1's character name
	 * @param c2
	 *            P2's character name
	 * @param name1
	 *            P1's AI name
	 * @param name2
	 *            P2's AI name
	 * @param num
	 *            the number of repeat count of this game
	 */
	public PyGame(PyManager manager, String c1, String c2, String name1, String name2, int num) {
		this.characterNames = new String[2];
		this.aiNames = new String[2];
		this.characterNames[0] = c1;
		this.characterNames[1] = c2;
		this.aiNames[0] = name1;
		this.aiNames[1] = name2;
		this.num = num;

		this.end = new Object();
		
		for (int i = 0; i < this.characterNames.length; i++)
			if (this.characterNames[i].toLowerCase().equals("rnd")) {
				FlagSetting.random[i] = true;
				this.characterNames[i] = LaunchSetting.randomCharacter();
			}

		// èµ·å‹•æƒ…å ±ã‚’æœ¬ä½“ã�«ã‚»ãƒƒãƒˆã�™ã‚‹
		LaunchSetting.deviceTypes[0] = InputManager.DEVICE_TYPE_AI;
		LaunchSetting.deviceTypes[1] = InputManager.DEVICE_TYPE_AI;
		LaunchSetting.characterNames[0] = this.characterNames[0];
		LaunchSetting.characterNames[1] = this.characterNames[1];
		LaunchSetting.aiNames[0] = name1;
		LaunchSetting.aiNames[1] = name2;
		LaunchSetting.repeatNumber = num;

		if (LaunchSetting.repeatNumber > 1) {
			FlagSetting.automationFlag = true;
		}
	}

	/**
	 * å¼•æ•°ã�§æŒ‡å®šã�—ã�Ÿãƒ—ãƒ¬ã‚¤ãƒ¤ãƒ¼ã�®ã‚­ãƒ£ãƒ©ã‚¯ã‚¿ãƒ¼ã�®ãƒ‡ãƒ¼ã‚¿ã‚’è¿”ã�™ï¼Ž
	 *
	 * @param playerNumber
	 *            ãƒ—ãƒ¬ã‚¤ãƒ¤ãƒ¼ç•ªå�·(true: P1; false: P2)
	 * @return æŒ‡å®šã�—ã�Ÿãƒ—ãƒ¬ã‚¤ãƒ¤ãƒ¼ã�®ã‚­ãƒ£ãƒ©ã‚¯ã‚¿ãƒ¼ã�®ãƒ‡ãƒ¼ã‚¿
	 */
	public String getCharacterName(boolean playerNumber) {
		return playerNumber ? this.characterNames[0] : this.characterNames[1];
	}

	/**
	 * å¼•æ•°ã�§æŒ‡å®šã�—ã�Ÿãƒ—ãƒ¬ã‚¤ãƒ¤ãƒ¼ã�®AIå��ã‚’è¿”ã�™ï¼Ž
	 *
	 * @param playerNumber
	 *            ãƒ—ãƒ¬ã‚¤ãƒ¤ãƒ¼ç•ªå�·(true: P1; false: P2)
	 * @return æŒ‡å®šã�—ã�Ÿãƒ—ãƒ¬ã‚¤ãƒ¤ãƒ¼ã�®AIå��
	 */
	public String getAIName(boolean playerNumber) {
		return playerNumber ? this.aiNames[0] : this.aiNames[1];
	}

	/**
	 * ã‚²ãƒ¼ãƒ ã�®ç¹°ã‚Šè¿”ã�—å›žæ•°ã‚’å�–å¾—ã�™ã‚‹ï¼Ž
	 *
	 * @return ã‚²ãƒ¼ãƒ ã�®ç¹°ã‚Šè¿”ã�—å›žæ•°
	 */
	public int getRepeatCount() {
		return this.num;
	}

}

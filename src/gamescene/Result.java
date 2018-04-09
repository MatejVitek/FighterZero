package gamescene;

import static org.lwjgl.glfw.GLFW.*;

import java.util.ArrayList;

import enumerate.GameSceneName;
import informationcontainer.AIContainer;
import informationcontainer.RoundResult;
import input.Keyboard;
import manager.GraphicManager;
import manager.InputManager;
import python.PyManager;
import setting.FlagSetting;
import setting.GameSetting;
import setting.LaunchSetting;
import util.LogWriter;

/**
 * ãƒªã‚¶ãƒ«ãƒˆç”»é�¢ã�®ã‚·ãƒ¼ãƒ³ã‚’æ‰±ã�†ã‚¯ãƒ©ã‚¹ï¼Ž
 */
public class Result extends GameScene {

	/**
	 * å�„ãƒ©ã‚¦ãƒ³ãƒ‰çµ‚äº†æ™‚ã�®P1, P2ã�®æ®‹ã‚Šä½“åŠ›, çµŒé�Žæ™‚é–“ã‚’æ ¼ç´�ã�™ã‚‹ãƒªã‚¹ãƒˆï¼Ž
	 */
	private ArrayList<RoundResult> roundResults;

	/**
	 * ç�¾åœ¨ã�®å¹´æœˆæ—¥, æ™‚åˆ»ã‚’è¡¨ã�™æ–‡å­—åˆ—ï¼Ž
	 */
	private String timeInfo;

	/**
	 * ãƒªã‚¶ãƒ«ãƒˆã�®è¡¨ç¤ºãƒ•ãƒ¬ãƒ¼ãƒ æ•°ï¼Ž
	 */
	private int displayedTime;

	/**
	 * ã‚¯ãƒ©ã‚¹ã‚³ãƒ³ã‚¹ãƒˆãƒ©ã‚¯ã‚¿ï¼Ž
	 */
	public Result() {
		// ä»¥ä¸‹4è¡Œã�®å‡¦ç�†ã�¯gamesceneãƒ‘ãƒƒã‚±ãƒ¼ã‚¸å†…ã‚¯ãƒ©ã‚¹ã�®ã‚³ãƒ³ã‚¹ãƒˆãƒ©ã‚¯ã‚¿ã�«ã�¯å¿…ã�šå�«ã‚�ã‚‹
		this.gameSceneName = GameSceneName.FIGHTING_MENU;
		this.isGameEndFlag = false;
		this.isTransitionFlag = false;
		this.nextGameScene = null;
		//////////////////////////////////////

		this.roundResults = new ArrayList<RoundResult>();
		this.timeInfo = "0";
		this.displayedTime = 0;
	}

	/**
	 * å�„ãƒ©ã‚¦ãƒ³ãƒ‰ã�®çµ�æžœã‚’æ ¼ç´�ã�—ã�Ÿãƒªã‚¹ãƒˆå�Šã�³ç�¾åœ¨ã�®æ™‚é–“æƒ…å ±ã‚’ã‚»ãƒƒãƒˆã�—, ãƒªãƒ—ãƒ¬ã‚¤ã‚·ãƒ¼ãƒ³ã‚’åˆ�æœŸåŒ–ã�™ã‚‹ã‚¯ãƒ©ã‚¹ã‚³ãƒ³ã‚¹ãƒˆãƒ©ã‚¯ã‚¿ï¼Ž
	 *
	 * @param roundResults
	 *            å�„ãƒ©ã‚¦ãƒ³ãƒ‰ã�®çµ�æžœã‚’æ ¼ç´�ã�—ã�Ÿãƒªã‚¹ãƒˆ
	 * @param timeInfo
	 *            ç�¾åœ¨ã�®æ™‚é–“æƒ…å ±
	 */
	public Result(ArrayList<RoundResult> roundResults, String timeInfo) {
		super();

		this.roundResults = new ArrayList<RoundResult>(roundResults);
		this.timeInfo = timeInfo;
		this.displayedTime = 0;
		roundResults.clear();
	}

	@Override
	public void initialize() {
		InputManager.getInstance().setSceneName(GameSceneName.RESULT);

		// pointãƒ•ã‚¡ã‚¤ãƒ«ã�®æ›¸ã��å‡ºã�—
		LogWriter.getInstance().outputResult(this.roundResults, LogWriter.CSV, this.timeInfo);
	}

	@Override
	public void update() {
		if (FlagSetting.enableWindow) {
			int[] positionX = new int[] { GameSetting.STAGE_WIDTH / 2 - 70, GameSetting.STAGE_WIDTH / 2 + 10 };

			for (int i = 0; i < this.roundResults.size(); i++) {
				String[] score = new String[] { String.valueOf(this.roundResults.get(i).getRemainingHPs()[0]),
						String.valueOf(this.roundResults.get(i).getRemainingHPs()[1]) };

				// ã‚¹ã‚³ã‚¢ã�®æ��ç”»
				GraphicManager.getInstance().drawString(score[0], positionX[0], 50 + i * 100);
				GraphicManager.getInstance().drawString(score[1], positionX[1], 50 + i * 100);

				// å‹�ã�¡ã‚„å¼•ã��åˆ†ã�‘ã�«å¿œã�˜ã�¦Win !ã‚„Drawã‚’ã‚¹ã‚³ã‚¢ã�®æ¨ªã�«å�°å­—
				switch (getWinPlayer(i)) {
				case 1:
					GraphicManager.getInstance().drawString("Win !", positionX[0] - 100, 50 + i * 100);
					break;
				case -1:
					GraphicManager.getInstance().drawString("Win !", positionX[1] + 80, 50 + i * 100);
					break;
				default:
					GraphicManager.getInstance().drawString("Draw", positionX[0] - 100, 50 + i * 100);
					GraphicManager.getInstance().drawString("Draw", positionX[1] + 80, 50 + i * 100);
					break;
				}
			}
		}

		endProcess();
	}

	@Override
	public void close() {
		this.roundResults.clear();
		this.displayedTime = 0;
	}

	/**
	 * P1, P2ã�®ã�©ã�¡ã‚‰ã�Œã��ã�®ãƒ©ã‚¦ãƒ³ãƒ‰ã�§å‹�ã�£ã�Ÿã�‹ã‚’è¿”ã�™ï¼Ž
	 *
	 * @param i ãƒ©ã‚¦ãƒ³ãƒ‰
	 *
	 * @return 0: å¼•ã��åˆ†ã�‘, 1: P1ã�®å‹�ã�¡, -1: P2ã�®å‹�ã�¡
	 */
	private int getWinPlayer(int i) {
		int[] remainingHPs = this.roundResults.get(i).getRemainingHPs();

		if (remainingHPs[0] == remainingHPs[1]) {
			return 0;
		} else if (remainingHPs[0] > remainingHPs[1]) {
			return 1;
		} else {
			return -1;
		}
	}

	/**
	 * å…¨AIã�®ç·�å½“ã‚Šå¯¾æˆ¦ã�Œçµ‚ã‚�ã�£ã�Ÿã�‹ã�©ã�†ã�‹ã‚’è¿”ã�™.
	 *
	 * @return {@code true} å…¨AIã�®ç·�å½“ã‚Šå¯¾æˆ¦ã�Œçµ‚ã‚�ã�£ã�Ÿ, {@code false} otherwise
	 */
	private boolean endRoundRobin() {
		return (AIContainer.p1Index + 1) == AIContainer.allAINameList.size()
				&& (AIContainer.p2Index + 1) == AIContainer.allAINameList.size();
	}

	/**
	 * Resultã‚·ãƒ¼ãƒ³ã�‹ã‚‰æ¬¡ã�®ã‚·ãƒ¼ãƒ³ã�«é�·ç§»ã�™ã‚‹éš›ã�®å‡¦ç�†ã‚’è¡Œã�†.
	 */
	private void endProcess() {
		// -aã‚„-nã‚’å¼•æ•°ã�«ã�—ã�¦èµ·å‹• or Repeat Countã‚’2ä»¥ä¸Šã�«ã�—ã�¦èµ·å‹•ã�—ã�Ÿå ´å�ˆã�®å‡¦ç�†
		if (FlagSetting.automationFlag || FlagSetting.allCombinationFlag || FlagSetting.py4j) {
			if (++this.displayedTime > 300) {
				// ã�¾ã� ç¹°ã‚Šè¿”ã�—å›žæ•°ã�Œæ®‹ã�£ã�¦ã�„ã‚‹å ´å�ˆ
				if (FlagSetting.automationFlag && LaunchSetting.repeatedCount + 1 < LaunchSetting.repeatNumber) {
					LaunchSetting.repeatedCount++;
					
					for (int i = 0; i < LaunchSetting.characterNames.length; i++)
						if (FlagSetting.random[i])
							LaunchSetting.characterNames[i] = LaunchSetting.randomCharacter();

					Launcher launcher = new Launcher(GameSceneName.PLAY);
					this.setTransitionFlag(true);
					this.setNextGameScene(launcher);

					// ã�¾ã� å…¨AIã�®ç·�å½“ã‚Šå¯¾æˆ¦ã�Œçµ‚ã‚�ã�£ã�¦ã�„ã�ªã�„å ´å�ˆ
				} else if (FlagSetting.allCombinationFlag) {
					if (++AIContainer.p1Index == AIContainer.allAINameList.size()) {
						AIContainer.p1Index = 0;
						AIContainer.p2Index++;
					}

					// ç·�å½“ã‚Šå¯¾æˆ¦ã�Œçµ‚äº†ã�—ã�Ÿã�‹ã�©ã�†ã�‹
					if (!endRoundRobin()) {
						Launcher launcher = new Launcher(GameSceneName.PLAY);
						this.setTransitionFlag(true);
						this.setNextGameScene(launcher);
					} else {
						this.setGameEndFlag(true);
					}

				} else if (FlagSetting.py4j) {
					synchronized (PyManager.python.getCurrentGame().end) {
						PyManager.python.getCurrentGame().end.notifyAll();
					}
					LaunchSetting.pyGatewayServer.close();
					Python python = new Python();
					this.setTransitionFlag(true);
					this.setNextGameScene(python);

					// æŒ‡å®šã�—ã�Ÿç¹°ã‚Šè¿”ã�—å›žæ•°åˆ†å¯¾æˆ¦ã�Œçµ‚ã‚�ã�£ã�Ÿå ´å�ˆ
				} else {
					this.setGameEndFlag(true);
				}
			}

			// é€šå¸¸ã�®å¯¾æˆ¦ã�®å ´å�ˆ, Enterã‚­ãƒ¼ã�ŒæŠ¼ã�•ã‚Œã‚‹ã�¾ã�§Resultç”»é�¢ã‚’è¡¨ç¤ºã�™ã‚‹
		} else {
			String string = "Press Enter key to return menu";
			GraphicManager.getInstance().drawString(string, GameSetting.STAGE_WIDTH / 2 - string.length() * 5 - 30,
					400);

			if (Keyboard.getKeyDown(GLFW_KEY_ENTER)) {
				HomeMenu homeMenu = new HomeMenu();
				this.setTransitionFlag(true);
				this.setNextGameScene(homeMenu);
			}
		}
	}
}

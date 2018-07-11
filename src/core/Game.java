package core;

import java.awt.Font;
import java.io.*;
import java.util.Random;
import java.util.logging.Level;
import java.util.logging.Logger;

import enumerate.BackgroundType;
import enumerate.GameSceneName;
import gamescene.HomeMenu;
import gamescene.Launcher;
import gamescene.Python;
import image.LetterImage;
import informationcontainer.AIContainer;
import loader.ResourceLoader;
import manager.GameManager;
import manager.GraphicManager;
import manager.InputManager;
import setting.FlagSetting;
import setting.GameSetting;
import setting.LaunchSetting;
import util.DeleteFiles;

/**
 * ă‚˛ă�Ľă� ă�®čµ·ĺ‹•ć�…ĺ ±ă‚’č¨­ĺ®šă�—, é–‹ĺ§‹ă�™ă‚‹ă‚˛ă�Ľă� ă‚·ă�Ľă�łă‚’č¨­ĺ®šă�™ă‚‹ă‚Żă�©ă‚ąďĽŽ
 */
public class Game extends GameManager {

	/**
	 * č¦Şă‚Żă�©ă‚ąă�§ă�‚ă‚‹GameManageră‚’ĺ�ťćśźĺŚ–ă�™ă‚‹ă‚Żă�©ă‚ąă‚łă�łă‚ąă��ă�©ă‚Żă‚żďĽŽ
	 */
	public Game() {
		super();
		InputManager.getInstance().registerAI("SRA", new ai.SRA());
	}

	/**
	 * čµ·ĺ‹•ć™‚ă�®ĺĽ•ć•°ă‚’ĺźşă�«, ă‚˛ă�Ľă� ă�®čµ·ĺ‹•ć�…ĺ ±ă‚’ă‚»ă��ă��ă�™ă‚‹.
	 *
	 * @param options
	 *            čµ·ĺ‹•ć™‚ă�«ĺ…ĄĺŠ›ă�—ă�źĺ…¨ă�¦ă�®ĺĽ•ć•°ă‚’ć Ľç´Ťă�—ă�źé…Ťĺ�—
	 */
	public void setOptions(String[] options) {
		// Reads the configurations here
		for (int i = 0; i < options.length; ++i) {
			switch (options[i]) {
			case "-a":
			case "--all":
				FlagSetting.allCombinationFlag = true;
				LaunchSetting.deviceTypes = new char[] { 1, 1 };
				break;
			case "-n":
			case "--number":
				LaunchSetting.repeatNumber = Integer.parseInt(options[++i]);
				FlagSetting.automationFlag = true;
				break;
			case "--a1":
				LaunchSetting.aiNames[0] = options[++i];
				LaunchSetting.deviceTypes[0] = InputManager.DEVICE_TYPE_AI;
				break;
			case "--a2":
				LaunchSetting.aiNames[1] = options[++i];
				LaunchSetting.deviceTypes[1] = InputManager.DEVICE_TYPE_AI;
				break;
			case "--c1":
				LaunchSetting.characterNames[0] = getCharacterName(options[++i]);
				break;
			case "--c2":
				LaunchSetting.characterNames[1] = getCharacterName(options[++i]);
				break;
			case "--r1":
				FlagSetting.random[0] = true;
				break;
			case "--r2":
				FlagSetting.random[1] = true;
				break;
			case "-da":
				FlagSetting.debugActionFlag = true;
				break;
			case "-df":
				FlagSetting.debugFrameDataFlag = true;
				break;
			case "-t":
				FlagSetting.trainingModeFlag = true;
				break;
			case "-del":
				DeleteFiles.getInstance().deleteFiles();
				break;
			case "--py4j":
				FlagSetting.py4j = true;
				break;
			case "--port":
				LaunchSetting.py4jPort = Integer.parseInt(options[++i]);
				break;
			case "--black-bg":
				LaunchSetting.backgroundType = BackgroundType.BLACK;
				break;
			case "--grey-bg":
				LaunchSetting.backgroundType = BackgroundType.GREY;
				break;
			case "--inverted-player":
				LaunchSetting.invertedPlayer = Integer.parseInt(options[++i]);
				break;
			case "--mute":
				FlagSetting.muteFlag = true;
				break;
			case "--disable-window":
			case "--fastmode":
				FlagSetting.enableWindow = false;
				FlagSetting.muteFlag = true;
				FlagSetting.fastModeFlag = true;
				FlagSetting.automationFlag = true;
				break;
			case "--json":
				FlagSetting.jsonFlag = true;
				break;
			case "--limithp":
				// --limithp P1_HP P2_HP
				FlagSetting.limitHpFlag = true;
				LaunchSetting.maxHp[0] = Integer.parseInt(options[++i]);
				LaunchSetting.maxHp[1] = Integer.parseInt(options[++i]);
				break;
			case "--err-log":
				FlagSetting.outputErrorAndLogFlag = true;
				break;
			default:
				Logger.getAnonymousLogger().log(Level.WARNING,
						"Arguments error: unknown format is exist. -> " + options[i] + " ?");
			}
		}

	}

	@Override
	public void initialize() {
		// ä˝żç”¨ă�•ă‚©ă�łă��ă�®ĺ�ťćśźĺŚ–
		Font awtFont = new Font("Times New Roman", Font.BOLD, 24);
		GraphicManager.getInstance().setLetterFont(new LetterImage(awtFont, true));

		createLogDirectories();

		// -nă�ľă�źă�Ż-aă�ŚćŚ‡ĺ®šă�•ă‚Śă�źă�¨ă�Ťă�Ż, ă�ˇă�‹ă�Ąă�Ľç”»éť˘ă�«čˇŚă�‹ă�šç›´ćŽĄă‚˛ă�Ľă� ă‚’Launchă�™ă‚‹
		if (FlagSetting.automationFlag || FlagSetting.allCombinationFlag) {
			if (FlagSetting.allCombinationFlag) {
				AIContainer.allAINameList = ResourceLoader.getInstance().loadFileNames("./data/ai", ".jar");

				if (AIContainer.allAINameList.size() < 2) {
					Logger.getAnonymousLogger().log(Level.INFO, "Cannot launch FightingICE with Round-robin mode.");
					this.isExitFlag = true;
				}
			}

			Launcher launcher = new Launcher(GameSceneName.PLAY);
			this.startGame(launcher);

		// -Pythonĺ�´ă�§čµ·ĺ‹•ă�™ă‚‹ă�¨ă�Ťă�Ż, Pythonă‚·ă�Ľă�łă�‹ă‚‰ă‚˛ă�Ľă� ă‚’é–‹ĺ§‹ă�™ă‚‹
		} else if (FlagSetting.py4j) {
			Python python = new Python();
			this.startGame(python);
			System.out.println("INIT_DONE");
			System.out.flush();
			// ä¸Šč¨�ä»Ąĺ¤–ă�®ĺ ´ĺ��, ă�ˇă�‹ă�Ąă�Ľç”»éť˘ă�‹ă‚‰ă‚˛ă�Ľă� ă‚’é–‹ĺ§‹ă�™ă‚‹
		} else {
			HomeMenu homeMenu = new HomeMenu();
			this.startGame(homeMenu);
		}
	}

	/**
	 * ĺĽ•ć•°ă�§ćŚ‡ĺ®šă�•ă‚Śă�źă‚­ă�Łă�©ă‚Żă‚żă�Ľĺ�Ťă�Śä˝żç”¨ĺŹŻč�˝ă‚­ă�Łă�©ă‚Żă‚żă�Ľĺ†…ă�«ă�‚ă‚‹ă�‹ă�©ă�†ă�‹ă‚’ć¤śç´˘ă�—, ă�‚ă‚‹ĺ ´ĺ��ă�Żă�ťă�®ĺ�Ťĺ‰Ťă‚’čż”ă�™ďĽŽ<br>
	 * ç„ˇă�‘ă‚Śă�°č­¦ĺ‘Šć–‡ă‚’ĺ‡şă�—, ZENă‚’ă�‡ă�•ă‚©ă�«ă��ă‚­ă�Łă�©ă‚Żă‚żă�Ľă�¨ă�—ă�¦čż”ă�™ďĽŽ
	 *
	 * @param characterName
	 *            ć¤śç´˘ă�™ă‚‹ă‚­ă�Łă�©ă‚Żă‚żă�Ľĺ�Ť
	 *
	 * @return ä˝żç”¨ă‚­ă�Łă�©ă‚Żă‚żă�Ľĺ�Ť
	 */
	private String getCharacterName(String characterName) {
		for (String character : GameSetting.CHARACTERS) {
			if (character.equals(characterName)) {
				return character;
			}
		}
		Logger.getAnonymousLogger().log(Level.WARNING,
				characterName + " does not exist. Please check the set character name.");
		return GameSetting.CHARACTERS[new Random().nextInt(GameSetting.CHARACTERS.length)];
	}

	/**
	 * Creates log directories if they do not exist.
	 */
	private void createLogDirectories() {
		new File("log").mkdir();
		new File("log/replay").mkdir();
		new File("log/point").mkdir();
	}

	@Override
	public void close() {
		this.currentGameScene = null;
	}

}

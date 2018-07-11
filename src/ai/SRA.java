package ai;

import java.util.Random;

import aiinterface.AIInterface;
import struct.*;

public class SRA implements AIInterface {
	
	private FrameData fd;
	private Key key;
	private boolean player;

	@Override
	public int initialize(GameData data, boolean player) {
		fd = new FrameData();
		key = new Key();
		this.player = player;
		return 0;
	}

	@Override
	public void getInformation(FrameData data) {
		fd = data;
	}

	@Override
	public void processing() {
		key.empty();
		if (fd.getEmptyFlag() || fd.getRemainingFramesNumber() <= 0) return;
		System.out.println(fd.getCharacter(!player).getSpeedX() + " " + fd.getCharacter(!player).getSpeedY());
		/*if (fd.getDistanceX() < 100) {
			key.A = new Random().nextInt(10) > 4;
			key.B = new Random().nextInt(10) > 4;
			key.C = new Random().nextInt(10) > 4;
		}
		else if (fd.getCharacter(player).getCenterX() < fd.getCharacter(!player).getCenterX())
			key.R = true;
		else
			key.L = true;*/
	}

	@Override
	public Key input() {
		return key;
	}

	@Override
	public void roundEnd(int p1HP, int p2HP, int framesFromRoundStart) {
	}

	@Override
	public void close() {
	}

}

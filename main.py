from sys import exit
import traceback
import argparse
import cv2
from agents import TagLedAgent
from utils import enable_vision, is_vision_enabled, set_yeti_07, is_valid_ip

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--agent', type=str, help='Agent to use. Valid values are: "tag".', default='tag')
    parser.add_argument('-v', '--vision', action='store_true', help='Whether showing plots is enabled')
    parser.add_argument('-n', '--num-games', type=int, help='Number of games to play', default=5)
    parser.add_argument("-it", "--chase", action='store_true') # False by default, add '-it' to set to True.
    parser.add_argument("-y7", "--is-yeti-07", action='store_true')
    parser.add_argument("-rbi", "--remote-bot-ip", type=str, help='IP of the other bot', default=None)
    
    # Parse the arguments
    args = parser.parse_args()
    agent_arg = args.agent
    is_it = args.chase
    num_games = args.num_games
    is_07 = args.is_yeti_07
    should_enable_vision = args.vision
    remote_ip = args.remote_bot_ip

    # Not sure if necessary
    # if not is_valid_ip(remote_ip):
    #     exit()

    # Yeti07 has a werid motor configuration. This flag fixes movement
    if is_07: set_yeti_07()

    print()
    # Check the ReadMe on how to see plots
    if should_enable_vision:
        print("MAIN : opening image windows")
        # Enable showing plots
        enable_vision()
        # Open a window to show the images in
        cv2.startWindowThread()
        cv2.namedWindow('image')
        cv2.namedWindow('secondary')
    
    agent = None
    try:
        if agent_arg == 'tag':
            agent = TagLedAgent(is_it, remote_ip)
        else:
            raise argparse.ArgumentError('Invalid argument for "--agent". Possible values are "tag".')
        
        print()
        input("MAIN :Agent {} is ready! Press Enter to start. ".format(agent.name))
        agent.play(num_games=num_games)

    except KeyboardInterrupt:
        pass

    except Exception as e:
        print("MAIN : an exception occured at runtime")
        print(traceback.format_exc())
        

    finally:
        agent.close_threads()
        if agent is not None:
            agent.camera.close()
            del agent.camera
            print('MAIN : closed the camera')
            # Always turn the motors off
            agent.yeti.SetLeftRightIndefinite(0,0)
            agent.yeti.ZB.MotorsOff()
            print('MAIN : motors off')
    
    if is_vision_enabled():
        # Close the window showing the images
        cv2.destroyAllWindows()

    exit()


if __name__ == "__main__":
    main()

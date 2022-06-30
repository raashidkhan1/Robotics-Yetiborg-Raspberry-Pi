from classes.YetiBorg import YetiBorg


def main():
    yeti = YetiBorg()
    yeti.SetLeftRightIndefinite(0, 0)
    yeti.ZB.MotorsOff()


if __name__ == "__main__":
    main()

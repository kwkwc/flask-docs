class TargetExistsException(Exception):
    def __init__(self, dest, *args: object) -> None:
        super().__init__(f"Target {dest} exists, use -f or --force to override")

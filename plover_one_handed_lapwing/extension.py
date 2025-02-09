from enum import auto, Enum

from plover import log

RIGHT_TO_LEFT = {
    "-F": "H-", "-P": "P-", "-L": "T-", "-T": "w",  "-D": "q",
    "-R": "R-", "-B": "W-", "-G": "K-", "-S": "S-", "-Z": "a",
    "-E": "O-", "-U": "A-",
}
LEFT_TO_RIGHT = {v: k for k, v in RIGHT_TO_LEFT.items()}
RIGHT_KEYS = RIGHT_TO_LEFT.keys()
LEFT_KEYS = LEFT_TO_RIGHT.keys()


class Hand(Enum):
    LEFT = auto()
    RIGHT = auto()


class OneHandedLapwingExtension:
    def __init__(self, engine):
        self._engine = engine
        self._engine.hook_connect("config_changed", self._on_config_changed)
        self._reset_stroke_state()
        # Previous machine stroke callback (if any).
        self._previous_machine_callback = None

    def start(self):
        self._on_config_changed()

    def stop(self):
        pass

    def _machine_stroke_callback(self, steno_keys):
        # Translate keys based on the current hand.
        if self._current_hand == Hand.LEFT:
            assert not self._left_keys
            # If we expected keys from teh left hand but got right, we need to remap them onto left keys.
            if steno_keys.issubset(RIGHT_KEYS):
                steno_keys = {RIGHT_TO_LEFT.get(k, k) for k in steno_keys}

            if set(["w"]) == steno_keys:
                # `w` alone indicates that there are no keys from the left hand in this stroke.
                self._left_keys = set()
            else:
                self._left_keys = steno_keys

            self._current_hand = Hand.RIGHT

        else:
            # If we expected keys from the right hand but got the left, we need to remap them onto right keys.
            if steno_keys.issubset(LEFT_KEYS):
                steno_keys = {LEFT_TO_RIGHT.get(k, k) for k in steno_keys}

            if set(["*"]) == steno_keys:
                # `*` on the right hand indicates that there are no keys from the right hand in this stroke.
                self._engine._on_stroked(self._left_keys)

            else:
                steno_keys.update(self._left_keys)
                self._engine._on_stroked(steno_keys)
                
            self._left_keys = set()
            self._current_hand = Hand.LEFT

    def _on_config_changed(self, *args):
        self._reset_stroke_state()

        system = self._engine.config["system_name"].lower()
        # Only override if we're using the one-handed Lapwing layout.
        if system != "one-handed lapwing stenotype":
            # If we're switching away from the one-handed system, restore old callback.
            if self._previous_machine_callback:
                log.info("Restoring machine stroke callback.")
                self._engine._machine.remove_stroke_callback(self._machine_stroke_callback)
                self._engine._machine.stroke_subscribers.insert(0, self._previous_machine_callback)
                self._previous_machine_callback = None
            return

        # Replace machine stroke callback with our interceptor.
        log.info("Overriding default machine stroke callback with one-handed interceptor.")
        # NOTE: This may play poorly with other plugins?
        self._previous_machine_callback = self._engine._machine.stroke_subscribers.pop(0)
        self._engine._machine.add_stroke_callback(self._machine_stroke_callback)

    def _reset_stroke_state(self):
        # Buffered left keys from the current stroke.
        self._left_keys = set()
        # Next hand from which we expect input.
        self._current_hand = Hand.LEFT

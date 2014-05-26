enum Mode {
  NONE,
  MOTOR,
  LED
};

int leftForwardPin = 5;
int leftBackwardPin = 6;
int rightForwardPin = 9;
int rightBackwardPin = 10;
int ledPin = 13;

int left = 0;
int right = 0;
unsigned int stage = 0;
unsigned char a = 'a';
unsigned char p = 'p';
int val = 0;
Mode mode = NONE;

// the setup routine runs once when you press reset:
void setup()  {
  // declare pin 9 to be an output:
  pinMode(leftForwardPin, OUTPUT);
  pinMode(leftBackwardPin, OUTPUT);
  pinMode(rightForwardPin, OUTPUT);
  pinMode(rightBackwardPin, OUTPUT);
  pinMode(ledPin, OUTPUT);
  analogWrite(leftForwardPin, 255);
  analogWrite(leftBackwardPin, 255);
  analogWrite(rightForwardPin, 255);
  analogWrite(rightBackwardPin, 255);
  Serial.begin(9600);
}

void reset() {
  stage = 0;
  mode = NONE;
}

void cmdLED() {
  if (val == '0') {
    digitalWrite(ledPin, LOW);
  } else if (val == '1') {
    digitalWrite(ledPin, HIGH);
  }
  reset();
}

void cmdMotor() {
  val = val - a;
  if ((val < 0) || (val > p - a)) {
    reset();
    return;
  }
  stage++;
  if (stage == 1) {
    left = (val << 4);
  } else if (state == 2) {
    left += val;
  } else if (stage == 3) {
    right = (val << 4);
  } else if (stage == 4) {
    right += val;
  } else {
    if ((val == 1) || (val == 3)) {
      left = -left;
    }
    if ((val == 2) || (val == 3)) {
      right = -right;
    }
    if (val > 3) {
      reset();
      return; // Invalid
    }

    if (left >= 0) {
      analogWrite(leftForwardPin, 255 - left);
      analogWrite(leftBackwardPin, 255);
    } else {
      analogWrite(leftForwardPin, 255);
      analogWrite(leftBackwardPin, left);
    }

    if (right >= 0) {
      analogWrite(rightForwardPin, 255 - right);
      analogWrite(rightBackwardPin, 255);
    } else {
      analogWrite(rightForwardPin, 255);
      analogWrite(rightBackwardPin, right);
    }
    reset();
  }
}

void loop()  {
  if (Serial.available() <= 0) {
    delay(1);
    return;
  }
  val = Serial.read();
  if (mode == MOTOR) {
    cmdMotor();
    return;
  } else if (mode == LED) {
    cmdLED();
    return;
  } else if (mode == NONE) {
    if (val == 'M') {
      mode = MOTOR;
    } else if (val == 'L') {
      mode = LED;
    }
    return;
  }
  reset();
}

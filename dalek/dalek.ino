enum Mode {
  NONE,
  MOTOR,
  LED
};

// Uncomment next line if you're Benjie
//#define L298N_MODE 1

#ifdef L298N_MODE
int leftForwardPin = 12;
int leftBackwardPin = 11;
int leftEnablePin = 10;
int rightForwardPin = 8;
int rightBackwardPin = 7;
int rightEnablePin = 6;
#else
int leftForwardPin = 5;
int leftBackwardPin = 6;
int rightForwardPin = 9;
int rightBackwardPin = 10;
#endif
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
  pinMode(ledPin, OUTPUT);
  pinMode(leftForwardPin, OUTPUT);
  pinMode(leftBackwardPin, OUTPUT);
  pinMode(rightForwardPin, OUTPUT);
  pinMode(rightBackwardPin, OUTPUT);
#ifdef L298N_MODE
  pinMode(leftEnablePin, OUTPUT);
  pinMode(rightEnablePin, OUTPUT);
  analogWrite(leftForwardPin, 0);
  analogWrite(leftBackwardPin, 0);
  analogWrite(leftEnablePin, 0);
  analogWrite(rightForwardPin, 0);
  analogWrite(rightBackwardPin, 0);
  analogWrite(leftEnablePin, 0);
#else
  analogWrite(leftForwardPin, 255);
  analogWrite(leftBackwardPin, 255);
  analogWrite(rightForwardPin, 255);
  analogWrite(rightBackwardPin, 255);
#endif
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
  } else if (stage == 2) {
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
#if L298N_MODE
    if (left >= 0) {
      digitalWrite(leftForwardPin, HIGH);
      digitalWrite(leftBackwardPin, LOW);
    } else {
      digitalWrite(leftForwardPin, LOW);
      digitalWrite(leftBackwardPin, HIGH);
    }

    if (right >= 0) {
      digitalWrite(rightForwardPin, HIGH);
      digitalWrite(rightBackwardPin, LOW);
    } else {
      digitalWrite(rightForwardPin, LOW);
      digitalWrite(rightBackwardPin, HIGH);
    }
    analogWrite(leftEnablePin, abs(left));
    analogWrite(rightEnablePin, abs(right));
#else
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
#endif
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

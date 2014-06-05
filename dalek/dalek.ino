#define BUFFER_SIZE 64

// Uncomment next line if you're Benjie
#define L298N_MODE 1

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

int bufferLength = 0;
char buffer[BUFFER_SIZE+1];

// the setup routine runs once when you press reset:
void setup()  {
  memset(buffer, 0, BUFFER_SIZE+1);
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

void cmdLED(char *str, int len) {
  if (len != 1) return;
  if (str[0] == '0') {
    digitalWrite(ledPin, LOW);
  } else if (str[0] == '1') {
    digitalWrite(ledPin, HIGH);
  }
}

void cmdMotor(char *str, int len) {
  if (len != 6) return;
  int left = 0;
  int right = 0;
  sscanf(str, "%-2x%-2x", &left, &right);
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
}

void shiftBuffer(int count) {
  memmove(buffer, buffer+count, BUFFER_SIZE - count);
  memset(buffer + BUFFER_SIZE - count, 0, count+1);
  bufferLength -= count;
}

void loop()  {
  int availableBytes = Serial.available();
  if (availableBytes <= 0) return;
  int maxLen = BUFFER_SIZE - bufferLength;
  if (availableBytes > maxLen) { // Ensure we don't overflow buffer
    availableBytes = maxLen;
  }
  Serial.readBytes(buffer + bufferLength, availableBytes);
  bufferLength += availableBytes;
  char *newlinePos;
  while (newlinePos = (char *)memchr(buffer, '\n', bufferLength)) {
    newlinePos[0] = '\0'; // Change \n to \0 temporarily
    if (buffer[0] == 'M') {
      cmdMotor(buffer+1, newlinePos - buffer - 1);
    } else if (buffer[0] == 'L') {
      cmdLED(buffer+1, newlinePos - buffer - 1);
    }
    shiftBuffer((newlinePos - buffer) + 1);
  }
  if (bufferLength == BUFFER_SIZE) {
    // No newlines, buffer full: start over
    shiftBuffer(BUFFER_SIZE);
  }
}

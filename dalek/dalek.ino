int leftForwardPin = 5;
int leftBackwardPin = 6;
int rightForwardPin = 9;
int rightBackwardPin = 10;
int left = 0;
int right = 0;
unsigned int stage = 0;
unsigned char a = 'a';
unsigned char p = 'p';
int val = 0;

// the setup routine runs once when you press reset:
void setup()  { 
  // declare pin 9 to be an output:
  pinMode(leftForwardPin, OUTPUT);
  pinMode(leftBackwardPin, OUTPUT);
  pinMode(rightForwardPin, OUTPUT);
  pinMode(rightBackwardPin, OUTPUT);
  analogWrite(leftForwardPin, 255);
  analogWrite(leftBackwardPin, 255);
  analogWrite(rightForwardPin, 255);
  analogWrite(rightBackwardPin, 255);
  Serial.begin(9600);
} 

// the loop routine runs over and over again forever:
void loop()  {
  
  if (!Serial.available() > 0) {
    return;
  }
  val = Serial.read();
  val = val - a;
  if ((val < 0) || (val > p - a)) {
    // Reset / invalid
    stage = 0;
    return;
  }
  if (stage == 0) {
    left = val * 16;
    if (left > 0) {
      left += 15; // 15*16 + 15 = 255
    }
    stage++;
    return;
  } else if (stage == 1) {
    right = val * 16;
    if (right > 0) {
      right += 15; // 15*16 + 15 = 255
    }
    stage++;
    return;
  } else {
    stage = 0; // Reset ready for next time
    if ((val == 1) || (val == 3)) {
      left = -left;
    }
    if ((val == 2) || (val == 3)) {
      right = -right;
    }
    if (val > 3) {
      return; // Invalid
    }
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
  
  delay(1);
  
  
  /*
  if (left >= 255) {
    if (right >= 255) {
      left = -255;
      right = -255;
    } else {
      right++;
    }
  } else {
    left++;
  }
  */
}


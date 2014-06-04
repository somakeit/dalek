#define L_FWD 5
#define L_BAK 6
#define R_FWD 9
#define R_BAK 10

//Errors
#define BAD_COMMAND    1
#define OUT_OF_BOUNDS  2
#define UNKNOWN        99

int setMotors(int l, int r);

char command[32];
/* Commands:
 "M -120 120\n"
  |||    |  |__ends with newline
  |||    |____right motor power as signed decimal string, ~half forward here.
  |||_________left motor power, ~half reverse here.
  ||__________NOTE: space delimiters are semi-optional
  |___________M for motor set command, no preceding chars allowed*/
  
void setup() {
  TCCR0B = TCCR0B & 0b11111000 | 1; //set PWM ports 5 & 6 to 62.5KHz AFFECTS MILIS AND DELAY
  TCCR1B = TCCR1B & 0b11111000 | 1; //set PWM ports 9 & 10 to ~31KHz
  
  pinMode(L_FWD, OUTPUT);
  pinMode(L_BAK, OUTPUT);
  pinMode(R_FWD, OUTPUT);
  pinMode(R_BAK, OUTPUT);
  
  Serial.begin(9600);
  /* Workaround TCCR0B setting and set timeout to 20ms, only hit if newline
   char lost or no data received, fast timout desired to unblock loop() and
   try again. It takes just over 2ms to fill the 32char buffer @ 9600 baud.*/
  Serial.setTimeout(1280); 
}

void loop() {
  byte len = Serial.readBytesUntil('\n', command, 31);
  command[len] = 0; //terminate string (srsly, arduino?)
  if (len) {
    int l = 0;
    int r = 0;
    int rc = UNKNOWN;
    if (2 == sscanf(command, "M %d %d", &l, &r)) {
      rc = setMotors(l, r);
      Serial.println(rc, DEC);
    } else {
      Serial.println(BAD_COMMAND, DEC);
    }
  }
}

int setMotors(int l, int r) {
  if ((l > 255) or (l < -255) or (r > 255) or (r < -255)) {
    return(OUT_OF_BOUNDS);
  }
  
  if (l >= 0) {
    analogWrite(L_BAK, 0);
    analogWrite(L_FWD, l);
  } else {
    analogWrite(L_FWD, 0);
    analogWrite(L_BAK, abs(l));
  }
  
  if (r >= 0) {
    analogWrite(R_BAK, 0);
    analogWrite(R_FWD, r);
  } else {
    analogWrite(R_FWD, 0);
    analogWrite(R_BAK, abs(r));
  }
  
  return(0);
}

// NeoPixel Ring simple sketch (c) 2013 Shae Erisson
// released under the GPLv3 license to match the rest of the AdaFruit NeoPixel library

#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
  #include <avr/power.h>
#endif
#define PIN            6
#define NUMPIXELS      40
Adafruit_NeoPixel strip = Adafruit_NeoPixel(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);
#include "mapSketch.h"
const byte numChars = 32;
char receivedChars[numChars]; // an array to store the received data
scoreEvent eventQueue[10];
void setup() {
  strip.begin(); // This initializes the NeoPixel library.
  Serial.begin(38400); //start Serial comm
  strip.show();
  for ( int i = 0 ; i<10 ; i++ ){
      scoreEvent ret = { 0,0,0,0,0,0,0,0,0 };  
      eventQueue[i] = ret;
  }
}

scoreEvent recieveEvent() {
  static byte ndx = 0;
  char endMarker = '\0'; //carriage return marks end of serial line
  char rc;
  while (Serial.available() > 0 ) {
    rc = Serial.read(); // reads in one byte from serial buffer
    if (rc != endMarker) { //continue to read in serial data
      receivedChars[ndx] = rc;
      ndx++;
      if (ndx >= numChars) {
        ndx = numChars - 1;
      }
    }
    else {
      receivedChars[ndx] = '\0'; // demarcate the end of OUR string.
      ndx = 0;
      byte r0=receivedChars[0]-1;
      byte r1=receivedChars[1]-1;
      byte r2=receivedChars[2]-1;
      byte r3=receivedChars[3]-1;
      byte r4=receivedChars[4]-1;
      byte r5=receivedChars[5]-1;
      byte r6=receivedChars[6]-1;
      byte r7=receivedChars[7]-1;
      scoreEvent ret = { r0,r1,r2,r3,r4,r5,r6,r7,1};
      return ret;
      }
    }
    scoreEvent ret = { 0,0,0,0,0,0,0,0,0 };
    return ret;
  }
void applyColor(byte city, byte r, byte g, byte b){
  strip.setPixelColor(city-1,strip.Color(r,g,b));
  strip.show();
}

void poop(){
  for (int i=0;i<40;i++){
      strip.setPixelColor(i,strip.Color(0,30,0));
    }
    strip.show();
    delay(500);
  for (int i=0;i<40;i++){
      strip.setPixelColor(i,strip.Color(30,0,0));
    }
    strip.show();
    delay(500);
    
  }
void loop() {
scoreEvent newEvent = recieveEvent();
if ( newEvent.cityNum > 0) { // if we got an event, add it in!
  for (int i=0 ; i<10 ; i++){
    if(eventQueue[i].points == 0 && eventQueue[i].cityNum ==0){
      eventQueue[i] = newEvent;
      break;
    }
  }
}
// now apply and clean all LEDs 
for (int i=0 ; i<10 ; i++){
  scoreEvent thisEvent = eventQueue[i];
  if(thisEvent.points == 0){ // either skip or clean
    if( thisEvent.cityNum != 0 ){ //clean out
      applyColor(thisEvent.cityNum,0,0,0); // blank the LED
      eventQueue[i] = { 0,0,0,0,0,0,0,0,0 };  // blank the queue entry
    }
  }
 else{
  if(thisEvent.first == 1){ //flash first color
    applyColor(thisEvent.cityNum,thisEvent.r1,thisEvent.g1,thisEvent.b1);
    eventQueue[i].first=0;  
  }
  else{ // flash second color
    applyColor(thisEvent.cityNum,thisEvent.r2,thisEvent.g2,thisEvent.b2);
    eventQueue[i].points -= 1;  
    eventQueue[i].first=1;  
    }
  } 
}

delay(500);
}

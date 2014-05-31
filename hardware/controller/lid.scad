lid_width = 225;
lid_hight = 137;

difference() {
  cube([lid_width, lid_hight, 2.5]);

  //screw holes
  translate([5, 5.5, -1]) cylinder(r = 2.5, h = 10);
  translate([lid_width - 5, 5.5, -1]) cylinder(r = 2.5, h = 10);
  translate([5, lid_hight - 5.5, -1]) cylinder(r = 2.5, h = 10);
  translate([lid_width -5, lid_hight - 5.5, -1]) cylinder(r = 2.5, h = 10);

  //fan place
  translate([lid_hight/2,lid_hight/2,-1]) {
    intersection() {
      cylinder(r = 64, h = 10, center = true);
      cube([116, 116, 10], center = true);
    }
    //fan mount
    translate([-52.5,-52.5,-1]) cylinder(r = 2.5, h = 10);
    translate([52.5,-52.5,-1]) cylinder(r = 2.5, h = 10);
    translate([-52.5,52.5,-1]) cylinder(r = 2.5, h = 10);
    translate([52.5,52.5,-1]) cylinder(r = 2.5, h = 10);
  }

  //exhaust vent
  translate([lid_hight + 14, lid_hight - 10, -1]) {
    for(j = [0 : 7 : 119]) {
      translate([0,-j,0]) for(i = [0 : 10 : 63]) {
        translate([i,0,0]) cylinder($fn = 6,  r = 2.5, h = 10);
      }
    }
  }
  translate([lid_hight + 19, lid_hight - 13.5, -1]) {
    for(j = [0 : 7 : 112]) {
      translate([0,-j,0]) for(i = [0 : 10 : 56]) {
        translate([i,0,0]) cylinder($fn = 6,  r = 2.5, h = 10);
      }
    }
  }
}
translate([lid_hight,lid_hight - 10,0])
  linear_extrude(3) text("Davros Industries", size = 5.5);
translate([lid_hight,lid_hight - 16,0])
  linear_extrude(3) text("Dalek Controller", size = 5.5);
translate([lid_hight,lid_hight - 22,0])
  linear_extrude(3) text("v0.7c", size = 5.5);
hull() {
  translate([lid_hight,lid_hight - 10,0])
    linear_extrude(2.5) text("Davros Industries", size = 5.5);
  translate([lid_hight,lid_hight - 16,0])
    linear_extrude(2.5) text("Dalek Controller", size = 5.5);
}
translate([lid_hight,lid_hight - 22,0])
  linear_extrude(2.5) scale([1,2,0]) hull() text("v0.7c", size = 5.5);
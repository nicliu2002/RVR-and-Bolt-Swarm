hold off
scatter(data.TX1,data.TY1,[] ,data.frame, "filled")
hold on
scatter(data.TX2,data.TY2,[] ,data.frame, "filled")
ylabel("Y Position")
xlabel("X Position")
text(data.TX1(2131)-200,data.TY1(2131)+100,"BOLT")
text(data.TX2(2131),data.TY2(2131),"RVR")
a = colorbar;
ylabel(a,'Time (frames)')
title("RVR and BOLT Simultaneous Commands")

hold off

% clears previous data 
clear all; 
clc; 

% creates array of two columns with infinite rows
pwmsize = [2,inf];

% opens text file
filePWM = fopen('','r');

%transposes data 
pwmdata = fscanf(filePWM,'%f %f', pwmsize);
pwmdata = pwmdata'; 

%seperates so much time and distance values
pwmvalue = pwmdata(:, 1);
timevalue = pwmdata(:,2); 

% code that plots values
plot(timevalue, pwmvalue); 

%labels for titles 
title('PWM time graph')
xlabel('PWM')
ylabel('time')

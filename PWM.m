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

%smoothing filter
pwm_smooth = smooth(timevalue, pwmvalue, 0.1, 'lowess'); 
plot(timevalue, pwm_smooth,'-r'); 

%labels for titles 
title('PWM time graph')
xlabel('Time(s)')
ylabel('PWM OutpUt (%)')

%improve visibility
ylim[0,100]

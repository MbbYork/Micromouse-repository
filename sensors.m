clear all; 
clc;

sizeA = [2,inf];
sizeB = [2,inf];
sizeC = [2,inf];

% opens and reads data from text files 
fileIDA = fopen('sensorA.txt','r'); 
fileIDB = fopen('sensorB.txt','r'); 
fileIDC = fopen('sensorC.txt','r'); 

% transposes data into column format
sensor1 = fscanf(fileIDA, '%f %f', sizeA); 
sensor2 = fscanf(fileIDB, '%f %f', sizeB); 
sensor3 = fscanf(fileIDC, '%f %f', sizeC); 

sensor1 = sensor1';
sensor2 = sensor2';
sensor3 = sensor3';

% code which seperates the time and distance values
timeA = sensor1(:, 1);
distanceA = sensor1(:,2);

timeB = sensor2(:, 1);
distanceB = sensor2(:,2);

timeC = sensor3(:,1); 
distanceC = sensor3(:,2);

% this plots the data
plot(distanceA, timeA)
hold on; 
plot(distanceB, timeB);
hold on; 
plot(distanceC, timeC);
hold off; 

% sets the labels for the graph
title("Distance measurements from VL6180 sensors")
xlabel("Time(s)")
ylabel("Distance(mm)")


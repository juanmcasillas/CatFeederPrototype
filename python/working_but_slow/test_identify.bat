@echo off
set P=C:\python27\python
set V=
%P% test_identify_kmeans.py %V% data/firulais.h264 
%P% test_identify_kmeans.py %V% data/firulais2.h264
%P% test_identify_kmeans.py %V% data/firulais3.h264
%P% test_identify_kmeans.py %V% data/firulais4.h264

%P% test_identify_kmeans.py %V% data/neko.h264
%P% test_identify_kmeans.py %V% data/neko2.h264

%P% test_identify_kmeans.py %V% data/eli.h264
%P% test_identify_kmeans.py %V% data/eli2.h264


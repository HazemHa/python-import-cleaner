# python-import-cleaner

##### the code has developed based on Chain of Responsibility

###### Regex(you can change based on your context)

1- select the file has a problem

```
(\/.\*\.[\w:]+)|([\w:]+\.\w+)
```

2- select the line in the file which has problem

```
r"\d+"
```

3- select the wrong import

```
r"from \w+\.\w+ import \w+"
```

### HOW IT WORK ?

1- generate a process and run the code.

```
subprocess.Popen(['python3.8', 'index.py'],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
```

2- open the stream with that process and receive the output and analysis it as a text.

```
output = process.stdout.readline()
```

3- change the flag status when the exception happened.

```
        if("Traceback" in str(request)):
            self.DebugLevel = True
```

4- keep pushing the output into cache until receiving full details about the expectation.

```
if("Error" in str(request)):
            return super().handle(self.cache)
        else:
            self.cache.append(request)
```

5- move to the next step to apply the regex to extract essential information.

6- open the file and comment on the line which has the problem and save it.

```
currentScript = open(request['path'].absolute(), "r+b")
```

++ confirm is that what we want.

```
 if(errorImport == currentErrorInFile):
            s_content[request['line']-1] = f"#{errorImport}".encode()
```

7- terminate the process and check again.

```
 if(result):
                print("the script has modified ")
                process.terminate()
                checkMissingFile(startDebuging)
```

### EXAMPLE

```
FULL OUTPUT :

Traceback (most recent call last):
File "index.py", line 1, in <module>
from setup import Setup
File "/home/yashazem/Documents/Yas-System/YAS-System/testDifferantVersionOfSystem/SensorDev/setup.py", line 2, in <module>
from Config.config import Config
File "/home/yashazem/Documents/Yas-System/YAS-System/testDifferantVersionOfSystem/SensorDev/Config/config.py", line 2, in <module>
from TrackingModuel.VirtualRelay import VirtualRelay
ModuleNotFoundError: No module named 'TrackingModuel'
```

##### SETP 1: OUTPUT

```
File "/home/yashazem/Documents/Yas-System/YAS-System/testDifferantVersionOfSystem/SensorDev/Config/config.py", line 2
```

##### SETP 2: OUTPUT

```
/home/yashazem/Documents/Yas-System/YAS-System/testDifferantVersionOfSystem/SensorDev/Config/config.py
```

##### SETP 3: OUTPUT

```
from TrackingModuel.VirtualRelay import VirtualRelay
```

##### SETP 4: OUTPUT

```
GO TO LINE NUMBER 2 => line 2 => then comment it# from TrackingModuel.VirtualRelay import VirtualRelay
```

## DONE

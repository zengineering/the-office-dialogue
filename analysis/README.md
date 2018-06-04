## Analysis of The Office dialogue

Kotlin apps for dialogue analysis.

Database interactions using [Exposed](https://github.com/JetBrains/Exposed).

### To build: 
```
./gradlew build
```

### To build and install: 
```
./install.sh
```

### To run correction and analysis:
```
./run.sh
```

### Individual commands:
#### correctDb
Applies corrections specified in a JSON resource file to the sqlite database created by *../acquisition* 
#### characterLineCounts
reads the database and exports a JSON file characterLineCounts.json of the form:
```
{
    character name:
        { season: 
            { episode: 
                number of lines of dialogue
            }
        }
}
```


#### Corrections needed in dialogue source
+ Names 
    + [x] misspellings
    + [ ] multiple characters with the same names
    + [ ] multiple speakers for the same line
+ Lines
    + [ ] normalize dash vs hyphen
    + [ ] normalize 3-periods vs ellipsis
    + [ ] quote ("", '') characters


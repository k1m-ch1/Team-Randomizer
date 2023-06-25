# Team-Randomizer
Randomizes teams with filters and different options

# TODO
## Abyss randomizer
### Character selection
- [x] logic on how toggling between local storage mode and using your characters from the db
- [x] logic for when user is logged in or not
- [x] updating the checkbox
- [x] implement the select all button
- [ ] toggle the checkbox when you click on the character-card
- [ ] refactor the code
### Filter
- [x] create the filtering interface
- [ ] filter the character selection interface when save
- [ ] storing it into a localStorage in the client's side
### Randomizer UI and logic
- [ ] create a randomize button and send it to an api
- [ ] write the randomize api and send it back to the client
- [ ] create a randomizer user interface that will display the characters you've just randomized
#### Modes
n means use all characters, distribute as evenly as possible
k is constant, uses user input
- Mode 1: Create k teams of k length
- Mode 2: Create n teams of constant k length 
- Mode 3: Create k teams of n length
- Mode 4: Select k characters to randomize (need to check for 0 < k <= max_characters)
- Mode 5: Select all characters to randomize 

All of this can be done using one function
### Randomizer history
- [ ] display a randomizer history for localStorage for not logged in and store in database if logged in
- [ ] create a UI that displays your history in your profile if logged in

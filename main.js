class Animal {
    animals = []
    constructor(name) {
        this.name = name;
    }
    speak() {
        console.log(this.name + " makes a noise.");
    }
    set_animals() {
        this.animals.push(this.name);
    }
    get_animals() {
        return this.animals;
    }
}

let animal1 = new Animal("Dog");
animal1.set_animals();
let animal2 = new Animal("Cat");
animal2.set_animals();
let animal3 = new Animal("Bird");
animal3.set_animals();
console.log(animal1.get_animals());
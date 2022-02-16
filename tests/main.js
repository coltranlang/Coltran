// closure

let make_counter = function () {
    let count = 0;
    return function () {
        return count++;
    };
};

let counter = make_counter();
console.log(counter());
console.log(counter());
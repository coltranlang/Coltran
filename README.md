<p>
  <h1>The Official Alden Programming Language</h1>
</p>

<p>
  Alden is an open source dynamic programming language that is designed to be simple, easy to learn, and easy to use to build efficient programs.
</p>

**DISCLAIMER:** This project is in it's very early development state, expect bugs and frequent breaking changes.

## Example
```ruby
class Wallet
    def __@init__(self)
        self.balance = 0
    end
    def deposit(self, amount)
        self.balance += amount
    end
    def withdraw(self, amount)
        if self.balance < amount:
            raise ValueError("Insufficient funds")
        end
        self.balance -= amount
    end
    def get_balance(self)
        return f"Your balance is $%{self.balance}"
    end
    def str(self)
        return f"Wallet balance: $%{self.balance}"
    end
end

```

## Documentation

See  [https://aldenlang.org/docs](https://aldenlang.org/docs) for documentation.

# Features

**Below is a list of features that are currently supported or planned for the future.**

- [x] Dynamic typing
- [x] Keyword arguments - **experimental**
- [x] Default arguments
- [x] Type annotations - **experimental**
- [x] Break and continue
- [ ] Class inheritance
- [x] Modules
- [x] Exception handling

see [features](https://aldenlang.org/features) for more language features.

### Issues

Please make sure to read the [Issue Reporting Guideline](/CONTRIBUTION.md#issue-reporting-guideline).

## Contribution

Please make sure to read the [Contributing guide](/CONTRIBUTION.md).

### License

[BSD-3-Clause](/LICENSE.md)
<br>
Copyright (c) 2021-present, Kehinde Akinsanya.

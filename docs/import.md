## How Alden imports works
#### Where does Alden look for a package?  

Alden looks for a package in the following order:
1. The standard library
2. The apm .alden_packages folder
3. The user's current working directory




- #### When you import a package, Alden will first look for the package from the standard library and check if the \__@init__.ald file exists. If it does, it will import the package. If it does not, it will look for the package from the apm .alden_packages folder and check if the \__@init__.ald file exists. If it does, it will import the package. If it does not, it will check for the package from the current working directory and check if the \__@init__.ald file exists. If it does, it will import the package. If it does not, an import error will be raised.
- **Note:** the module name is case sensitive.
<br>

## Importing a package from another package
To import the `location` package from the `driver` package, you can use the following syntax:

See above for where Alden looks for the package.
```python
import driver.location
```

- Windows: C:\Users\username\Desktop\Alden\driver\location\\\__@init__.ald


## Importing a specific module from a package
To import the `config` module from the `driver` package, you can use the following syntax:
```python
import driver.config.ald
```
- config will be set as the module name.
- Windows: C:\Users\username\Desktop\Alden\driver\config.ald

**Note:** The `.ald` extension tells Alden that the file is a module not a package.


## Importing only a part of a package
To import the `get_address` function from the location package, you can use the following syntax:
```python   
from driver.location import get_address
```

## Renaming a module
To rename the `get_address` function to `address`, you can use the following syntax:
```python
from driver.location import get_address as address
```
To rename a package, you can use the following syntax:
```python
import math as m
println(m.pi)
```
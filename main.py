class Coffee_order:
    def __init__(self, options: object) -> None:
        self.__options = options

    def __str__(self) -> str:
        return self.__options.get("description")


# some details of coffee is not included bcs of unknown


class Coffee_order_builder:
    def __init__(self) -> None:
        self.__currency = "ju"  # abstractly
        self.__Coffee_order = Coffee_order
        self.__options = self.__get_default_options()
        self.__default_values = {
            "cost": {
                "base": {
                    "espresso": 200,
                    "americano": 250,
                    "latte": 300,
                    "cappuccino": 320,
                },
                "milk": {
                    "whole": 30,
                    "skim": 30,
                    "oat": 60,
                    "soy": 50,
                },
                "syrup": 40,
                "ice": 0.2,
                "size_multiplier": {
                    "small": 1.0,
                    "medium": 1.2,
                    "large": 1.4,
                },
            },
            "limit": {
                "syrup": 4,
                "sugar": 5,
            },
        }

    def __str__(self) -> None:
        description = self.__options.get("description")
        return (
            description
            if description
            else f"Coffee order: {self.__options.get('price'):.2f}"
        )

    def __get_default_options(self) -> object:
        return {
            "base": "",
            "size": "",
            "milk": None,
            "syrups": (),
            "sugar": 0,
            "iced": False,
            "price": 0,
            "description": "",
        }

    def __get_options_value(
        self, key: str
    ) -> any:  # flat getter, not __getattr__, no nested values
        return self.__options.get(key)

    def __get_default_option(self, first_key: str, *last_keys: str) -> any:
        res = self.__default_values.get(first_key)
        for key in last_keys:
            res = res.get(key)
        return res

    def __set_options_value(
        self, key: str, value: any
    ) -> None:  # flat setter, not __setattr__, no nested values
        self.__options[key] = value

    def __change_drink_option(self, key: str, value: any) -> None:
        self.__set_options_value(key, value)
        self.__regenerate_price()
        self.__regenerate_description()

    def __regenerate_description(self) -> None:
        basic = []
        if self.__options.get("iced", False):
            basic.append("iced")

        basic.append(self.__options.get("size"))
        basic.append(self.__options.get("base"))
        subs = []
        # faster computing way

        if self.__options.get("milk"):
            subs.append(f"{self.__options.get('milk')} milk")

        syrups = list(syrup for syrup in self.__options.get("syrups", [""]))
        if syrups:
            subs.append(
                f"{', '.join(syrups)} {'syrup' if len(syrups) == 1 else 'syrups'}"
            )

        if self.__options.get("sugar"):
            subs.append(f"{self.__options.get('sugar')} spoonce of sugar")

        price = f"costing {self.__options.get('price')} {self.__currency}"
        self.__set_options_value(
            "description",
            f"{' '.join(basic)}{' with ' + ' and '.join(subs) if subs else ''} {price}",
        )

    def __regenerate_price(self) -> None:
        get_opt = self.__get_options_value
        get_def = self.__get_default_option
        # static price for any type of syrup
        new_price = (
            get_def("cost", "base").get(get_opt("base"), 0)
            + get_def("cost", "milk").get(get_opt("milk"), 0)
            + get_def("cost", "syrup") * len(get_opt("syrups"))
        ) * (get_def("cost", "size_multiplier").get(get_opt("size"), 0)) + (
            get_def("cost", "ice") if get_opt("iced") else 0
        )
        self.__set_options_value("price", new_price)

    def set_base(self, base: str) -> "Coffee_order_builder":
        """Sets the base coffee type.
        Args:
                base: coffee type from available options
        Returns:
                self for the call chain"""
        if base in self.__default_values.get("cost").get("base"):
            self.__change_drink_option("base", base)
        return self

    def set_size(self, size: str) -> "Coffee_order_builder":
        """Sets the drink size.
        Args:
            size: size from available options
        Returns:
            self for the call chain"""
        if size in self.__default_values.get("cost").get("size_multiplier"):
            self.__change_drink_option("size", size)
        return self

    def set_milk(self, milk: str) -> "Coffee_order_builder":
        """Sets the milk type.
        Args:
            milk: milk type from available options
        Returns:
            self for the call chain"""
        if milk in self.__default_values.get("cost").get("milk"):
            self.__change_drink_option("milk", milk)
        return self

    def add_syrup(self, name: str) -> "Coffee_order_builder":
        """Adds syrup to the drink if the limit has not been exceeded and there are no duplicates.
        Args:
            name: syrup name
        Returns:
            self for the call chain"""
        if type(name) == str:
            syrups = self.__get_options_value("syrups")
            if self.__default_values.get("limit").get("syrup") > len(syrups):
                if name not in syrups:
                    self.__change_drink_option("syrups", (*syrups, name))
        return self

    def set_sugar(self, teaspoons: int) -> "Coffee_order_builder":
        """Sets the amount of sugar in teaspoons.
        Args:
            teaspoons: Number of teaspoons of sugar
        Returns:
            self for the call chain"""
        if type(teaspoons) == int:
            if self.__default_values.get("limit").get("sugar") >= teaspoons:
                self.__change_drink_option("sugar", teaspoons)
        return self

    def set_iced(self, iced: bool = True) -> "Coffee_order_builder":
        """Sets the drink's chilling.
        Args:
            iced: True for a chilled drink
        Returns:
            self for the call chain"""
        if type(iced) == bool:
            self.__change_drink_option("iced", iced)
        return self

    def clear_extras(self) -> "Coffee_order_builder":
        """Clears all additional options, preserving the base and size.
        Returns:
            self for the call chain"""
        self.__options = {
            **self.__get_default_options(),
            "base": self.__options.get("base"),
            "size": self.__options.get("size"),
        }
        self.__regenerate_price()
        self.__regenerate_description()
        return self

    def build(self) -> Coffee_order:
        """Creates a final coffee order with validation of required fields.
        Returns:
            Coffee_order object
        Raises:
            ValueError: if base or size is not set"""
        if not self.__get_options_value("base"):
            raise ValueError("Drink should have base")
        if not self.__get_options_value("size"):
            raise ValueError("Drink should have size")
        return self.__Coffee_order({**self.__options})



def test_basic_coffee_creation():
    """Basic Coffee Creation Test"""
    builder = Coffee_order_builder()
    coffee1 = builder.set_base("espresso").set_size("small").build()
    coffee2 = builder.build()
    assert coffee1 != coffee2
    assert "espresso" in str(coffee1)
    assert "small" in str(coffee1)
    assert "espresso" in str(coffee2)
    assert "small" in str(coffee2)


def test_empty_base_error():
    """Coffee with empty base"""
    builder = Coffee_order_builder()
    try:
        builder.set_size("large").build()
        assert False, "Should raise ValueError for empty base"
    except ValueError as e:
        assert "base" in str(e)

def test_empty_size_error():
    """Coffee with empty size"""
    builder = Coffee_order_builder()
    try:
        builder.set_base("latte").build()
        assert False, "Should raise ValueError for empty size"
    except ValueError as e:
        assert "size" in str(e)

def test_coffee_with_milk():
    """Coffee with milk test"""
    builder = Coffee_order_builder()
    coffee = str(builder.set_base("latte").set_size("medium").set_milk("oat").build())
    assert "latte" in coffee
    assert "medium" in coffee
    assert "oat" in coffee

def test_coffee_with_syrups():
    """Coffee with syrups test"""
    builder = Coffee_order_builder()
    coffee = str(builder.set_base("cappuccino")
        .set_size("large")
        .add_syrup("vanilla")
        .add_syrup("caramel")
        .build())
    assert "cappuccino" in coffee
    assert "large" in coffee
    assert "vanilla" in coffee
    assert "caramel" in coffee

def test_coffee_with_sugar():
    """Coffee with sugar test"""
    builder = Coffee_order_builder()
    coffee = str(builder.set_base("americano").set_size("small").set_sugar(3).build())
    assert "americano" in coffee
    assert "small" in coffee
    assert "3 spoonce of sugar" in coffee


def test_iced_coffee():
    """Coffee with ice test"""
    builder = Coffee_order_builder()
    coffee = str(builder.set_base("latte").set_size("medium").set_iced(True).build())
    assert "latte" in coffee
    assert "medium" in coffee
    assert "iced" in coffee


def test_complex_coffee():
    """Complex order yest"""
    builder = Coffee_order_builder()
    coffee = str(builder.set_base("latte")
        .set_size("large")
        .set_milk("soy")
        .add_syrup("vanilla")
        .add_syrup("hazelnut")
        .set_sugar(2)
        .set_iced(True)
        .build())
    assert "latte" in coffee
    assert "large" in coffee
    assert "soy" in coffee
    assert "vanilla" in coffee
    assert "hazelnut" in coffee
    assert "2 spoonce of sugar" in coffee
    assert "iced" in coffee

def test_clear_extras():
    """Clear extras test"""
    builder = Coffee_order_builder()
    coffee1 = str(builder.set_base("cappuccino")
        .set_size("medium")
        .set_milk("oat")
        .add_syrup("caramel")
        .set_sugar(4)
        .build())
    
    coffee2 = str(builder.set_base("cappuccino")
        .set_size("medium")
        .clear_extras()
        .build())
    assert "oat" in str(coffee1)
    assert "caramel" in str(coffee1)
    assert "4 spoonce of sugar" in str(coffee1)
    assert "oat" not in str(coffee2)
    assert "caramel" not in str(coffee2)

def test_syrup_limit():
    """Syrup Limit Test"""
    builder = Coffee_order_builder()
    coffee = str(builder.set_base("latte")
        .set_size("small")
        .add_syrup("vanilla")
        .add_syrup("caramel")
        .add_syrup("hazelnut")
        .add_syrup("rose")
        .add_syrup("extra")
        .build())
    assert "vanilla" in coffee
    assert "caramel" in coffee
    assert "hazelnut" in coffee
    assert "extra" not in coffee

def test_sugar_limit():
    """Sugar Limit Test"""
    builder = Coffee_order_builder()
    coffee = str(builder.set_base("espresso").set_size("small").set_sugar(10).build())
    assert "10 spoonce of sugar" not in coffee
    assert "espresso" in coffee

def test_price_calculation():
    """Test cost"""
    builder = Coffee_order_builder()
    coffee = str(builder.set_base("latte")
        .set_size("large")
        .set_milk("oat")
        .add_syrup("vanilla")
        .add_syrup("caramel")
        .set_iced()
        .set_sugar(3)
        .build())
    coffee_str = coffee
    assert "616.2" in coffee_str

if __name__ == "__main__":
    test_basic_coffee_creation()
    test_empty_base_error()
    test_empty_size_error()
    test_coffee_with_milk()
    test_coffee_with_syrups()
    test_coffee_with_sugar()
    test_iced_coffee()
    test_complex_coffee()
    test_clear_extras()
    test_syrup_limit()
    test_sugar_limit()
    test_price_calculation()
    print("All tests passed!")
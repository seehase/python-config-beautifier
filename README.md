# Config Beautifier

Config Beautifier is a Python script that automatically formats and beautifies configuration files. It's designed to help you maintain clean, readable, and consistent `.conf` files with minimal effort. The script intelligently handles sections, subsections, key-value pairs, and comments, ensuring proper indentation and spacing throughout your configuration files.

This tool is especially useful for projects where multiple developers contribute to the same configuration files, as it enforces a uniform style and structure. By automating the formatting process, you can focus on what matters—the configuration itself—while the script takes care of the rest.

## What it does

The script parses configuration files and applies a set of formatting rules to ensure consistency and readability. Key features include:

- **Intelligent Indentation**: Automatically adjusts the indentation of sections, subsections, and key-value pairs to reflect their hierarchical structure.
- **Consistent Spacing**: Enforces consistent spacing around key-value pairs and adds blank lines where needed to improve readability.
- **Comment Handling**: Properly aligns comments with their corresponding sections, ensuring they remain correctly positioned after formatting.
- **Duplicate Section Warnings**: Detects and warns about duplicate sections, helping you avoid potential configuration conflicts.

## Usage

To use the script, simply run it from the command line and provide the path to your configuration file. You can either overwrite the original file or specify a new output file.

### Basic Usage

To format a file in place, run the following command:

```bash
./config_beautifier.py your_config.conf
```

### Writing to a New File

To save the formatted output to a new file, use the `-o` or `--output` option:

```bash
./config_beautifier.py your_config.conf -o formatted_config.conf
```

### Custom Indentation

You can also customize the indentation level by using the `--indent` option. The default is 4 spaces.

```bash
./config_beautifier.py your_config.conf --indent 2
```

## Before vs. After

Here’s a quick look at how the Config Beautifier can transform a messy configuration file into a clean and organized one.

### Before

```
# Skin specific configuration
# -----------------------------------------------------------------------------
#
# Dear user: This is probably the only section you need to edit
#
[section1]
# comment
# comment
key1 = value1

#comment
[[subsection1]]
key1 = value1
# comment
key2 = value2

# Embedded iFrames and images
# -------------------------------------------------------------------------
# Here you can add your own iFrames or images to be displayed as cards on the "current" page.
# Section names must start with iFrame or image and must be unique. Doesn't need to be numbered.
# Feel free to use any name like iFrameMyWebsite or imageMyLogo, just keep it same in the embedded_order list above.
#
[[subsection2]]
key1 = value3

[[subsection3]]
key1 = value4

[[subsection4]]
key1 = value1
[[[subsection1]]]
key1 = value1
key5 = value5

[[subsection5]]
[[[subsection1]]]
[[[[subsection1]]]]
key7 = value7

[[[subsection2]]]
key1 = value1

# comment				                
[section2]        
key1 = value1
[[subsection1]]
key1 = value1
```

### After

```
# Skin specific configuration
# -----------------------------------------------------------------------------
#
# Dear user: This is probably the only section you need to edit
#
[section1]
    # comment
    # comment
    key1 = value1

    #comment
    [[subsection1]]
        key1 = value1
        # comment
        key2 = value2

    # Embedded iFrames and images
    # -------------------------------------------------------------------------
    # Here you can add your own iFrames or images to be displayed as cards on the "current" page.
    # Section names must start with iFrame or image and must be unique. Doesn't need to be numbered.
    # Feel free to use any name like iFrameMyWebsite or imageMyLogo, just keep it same in the embedded_order list above.
    #
    [[subsection2]]
        key1 = value3

    [[subsection3]]
        key1 = value4

    [[subsection4]]
        key1 = value1

        [[[subsection1]]]
            key1 = value1
            key5 = value5

    [[subsection5]]
        [[[subsection1]]]
            [[[[subsection1]]]]
                key7 = value7

        [[[subsection2]]]
            key1 = value1

# comment
[section2]
    key1 = value1

    [[subsection1]]
        key1 = value1
```

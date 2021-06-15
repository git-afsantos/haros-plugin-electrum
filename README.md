# HAROS Electrum Plugin

This is a [HAROS](https://github.com/git-afsantos/haros/) plugin that converts computation graphs annotated with [HPL](https://github.com/git-afsantos/hpl-specs/) properties into formal models suitable for model checking with [Electrum](https://github.com/haslab/Electrum2).

## Installing

To install this package, make sure that you have Python 2.7 or greater.
It is assumed that you **have Electrum installed or otherwise available** in your system, before using this tool.

You can either install a pre-packaged release,

```bash
pip install haros-plugin-electrum
```

Or you can install from source.

```bash
git clone https://github.com/git-afsantos/haros-plugin-electrum.git
cd haros-plugin-electrum
pip install -e .
```

## Usage

Start by defining annotated configurations in HAROS project files, as you normally would.

In the plugin-specific section of the file, you have to provide a path to the Electrum `.jar` file.
In addition, you can also specify `scope` limits for the Electrum Analyzer.

```yaml
%YAML 1.1
---
project: Fictibot
packages:
  - fictibot_drivers
  - fictibot_controller
  - fictibot_multiplex
  - fictibot_msgs
configurations:
  multiplex:
    launch:
      - fictibot_controller/launch/multiplexer.launch
    user_data:
      haros_plugin_electrum:
        jar:
          path: /full/path/to/electrum.jar
          env: ENV_VAR_NAME_WITH_PATH
        scope:
          time: 10
          msgs: 9
          values: 4
```

In the example above, we have two ways of defining a path to the Electrum Analyzer:

- `path` specifies a full path to the executable `.jar`.
- `env` specifies an environment variable holding the path to the `.jar` file.

It suffices to specify only one of them.


## Bugs, Questions and Support

Please use the [issue tracker](https://github.com/git-afsantos/haros-plugin-electrum/issues).

## Citing

See [CITING](./CITING.md).

## Contributing

See [CONTRIBUTING](./CONTRIBUTING.md).

## Acknowledgment

Until March 2021, this work was financed by the ERDF – European Regional Development Fund through the Operational Programme for Competitiveness and Internationalisation - COMPETE 2020 Programme and by National Funds through the Portuguese funding agency, FCT - Fundação para a Ciência e a Tecnologia within project PTDC/CCI-INF/29583/2017 (POCI-01-0145-FEDER-029583).

{
  description = "monz — Monzo CLI (GraemeF fork with pinned pymonzo)";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

  outputs =
    { nixpkgs, ... }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      forAllSystems =
        f:
        nixpkgs.lib.genAttrs systems (
          system:
          f {
            inherit system;
            pkgs = nixpkgs.legacyPackages.${system};
          }
        );

      mkPymonzo =
        python: pkgs:
        python.pkgs.buildPythonPackage rec {
          pname = "pymonzo";
          version = "2.2.1";
          pyproject = true;
          src = pkgs.fetchPypi {
            inherit pname version;
            hash = "sha256-bmVURHS8jJ3YGCZb1DpMIva87MvV3JB80clUFTXJalg=";
          };
          patches = [
            ./patches/pymonzo-loop-oauth-callback.patch
            ./patches/pymonzo-cursor-since.patch
          ];
          build-system = [ python.pkgs.flit-core ];
          dependencies = with python.pkgs; [
            authlib
            httpx
            pydantic
            pydantic-settings
          ];
          doCheck = false;
        };

      runtimeDeps =
        python: pkgs:
        (with python.pkgs; [
          babel
          click
          click-default-group
          rich
          rich-click
        ])
        ++ [ (mkPymonzo python pkgs) ];

      mkMonz =
        pkgs:
        let
          python = pkgs.python313;
        in
        python.pkgs.buildPythonApplication {
          pname = "monz";
          version = "1.1.1";
          pyproject = true;
          src = ./.;
          build-system = [ python.pkgs.flit-core ];
          dependencies = runtimeDeps python pkgs;
          doCheck = false;
        };

      mkDevShell =
        pkgs:
        let
          python = pkgs.python313;
        in
        pkgs.mkShell {
          packages = [
            (python.withPackages (
              ps:
              (runtimeDeps python pkgs)
              ++ (with ps; [
                polyfactory
                pytest
                pytest-mock
                time-machine
              ])
            ))
          ];
        };
    in
    {
      packages = forAllSystems (
        { pkgs, ... }:
        {
          default = mkMonz pkgs;
        }
      );

      devShells = forAllSystems (
        { pkgs, ... }:
        {
          default = mkDevShell pkgs;
        }
      );

      apps = forAllSystems (
        { system, pkgs }:
        {
          default = {
            type = "app";
            program = "${mkMonz pkgs}/bin/monz";
          };
        }
      );
    };
}

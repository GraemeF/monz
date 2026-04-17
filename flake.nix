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

      mkMonz =
        pkgs:
        let
          python = pkgs.python313;
          pymonzo = python.pkgs.buildPythonPackage rec {
            pname = "pymonzo";
            version = "2.2.1";
            pyproject = true;
            src = pkgs.fetchPypi {
              inherit pname version;
              hash = "sha256-bmVURHS8jJ3YGCZb1DpMIva87MvV3JB80clUFTXJalg=";
            };
            patches = [ ./patches/pymonzo-loop-oauth-callback.patch ];
            build-system = [ python.pkgs.flit-core ];
            dependencies = with python.pkgs; [
              authlib
              httpx
              pydantic
              pydantic-settings
            ];
            doCheck = false;
          };
        in
        python.pkgs.buildPythonApplication {
          pname = "monz";
          version = "1.1.1";
          pyproject = true;
          src = ./.;
          build-system = [ python.pkgs.flit-core ];
          dependencies =
            (with python.pkgs; [
              babel
              click
              click-default-group
              rich
              rich-click
            ])
            ++ [ pymonzo ];
          doCheck = false;
        };
    in
    {
      packages = forAllSystems (
        { pkgs, ... }:
        {
          default = mkMonz pkgs;
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

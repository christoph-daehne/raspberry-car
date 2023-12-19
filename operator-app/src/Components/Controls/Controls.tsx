import { Direction } from "../../Direction";

function Controls({
  activeDirection,
  onChange,
}: {
  activeDirection: Direction,
  onChange: (direction: Direction) => void
}) {
  return (
    <>
      <div class="row">
        <button
          onMouseUp={() => onChange(Direction.None)}
          onMouseDown={() => onChange(Direction.Foreward)}
          classList={{ active: activeDirection === Direction.Foreward }}
        >
          Foreward
        </button>
      </div>
      <div class="row my">
        <button
          onMouseUp={() => onChange(Direction.None)}
          onMouseDown={() => onChange(Direction.Left)}
          classList={{ active: activeDirection === Direction.Left }}
        >
          Left
        </button>
        <button
          onMouseUp={() => onChange(Direction.None)}
          onMouseDown={() => onChange(Direction.Back)}
          classList={{ active: activeDirection === Direction.Back, mx: true }}
        >
          Back
        </button>
        <button
          onMouseUp={() => onChange(Direction.None)}
          onMouseDown={() => onChange(Direction.Right)}
          classList={{ active: activeDirection === Direction.Right }}
        >
          Right</button>
      </div>
    </>
  );
}

export default Controls;

import { render, screen } from "@testing-library/react";
import ReadinessScore from "@/components/dashboard/ReadinessScore";

describe("ReadinessScore", () => {
  it("displays the score number", () => {
    render(<ReadinessScore score={82} label="Optimal" color="text-emerald-400" />);
    expect(screen.getByText("82")).toBeInTheDocument();
    expect(screen.getByText("Optimal")).toBeInTheDocument();
  });
  it("renders low score", () => {
    render(<ReadinessScore score={35} label="Low" color="text-rose-400" />);
    expect(screen.getByText("35")).toBeInTheDocument();
  });
});

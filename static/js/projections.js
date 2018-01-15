function calculateTargetScore(assignments, desired, pe, pp) {
    var upcoming_pp = 0;
    for (var i = 0; i < assignments.length; i++) {
      upcoming_pp += assignments[i]['points_possible'];
    };
    var tme = desired * (pp + upcoming_pp) / 100 - pe;
    var a1_pme = (assignments[0]['points_possible'] * tme) / upcoming_pp;
    var percentage = a1_pme / assignments[0]['points_possible'] * 100
    return (Math.ceil(percentage * 100) / 100);
}
function calculateWeightedTargetScore(categories, desired) {
    var num_sum = 0;
    var denominator = 0;
    for (var i = 0; i < categories.length; i++) {
      if (categories[i]['num_assignments'] > 0) {
          num_sum += (categories[i]['weight'] * categories[i]['sum']) / (categories[i]['num_assignments'] + categories[i]['upcoming'].length);
          denominator += (categories[i]['weight'] * categories[i]['upcoming'].length) / (categories[i]['num_assignments'] + categories[i]['upcoming'].length);
      }
      else {
          num_sum += 100.0;
          denominator += categories[i]['weight'];
      }
    }
    var numerator = desired - num_sum
    return (Math.ceil(numerator / denominator * 100) / 100);
}
function updateTargetScore(targetScore, element) {
    if (targetScore < 0) {
      var text = "Not Possible";
    }
    else if (targetScore > 100) {
      var text = "100+%";
    }
    else {
      var text = targetScore + "%";
    }
    targets = element.querySelectorAll('.projection-target');
    for (var i = 0; i < targets.length; i++) {
      targets[i].innerHTML = text;
    }
}